import re

from django.core.cache import cache
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from apps.store.models import Brand, Category, MainCategory, Product

# The nav and catalogue menus in base.html are context processors that cache
# under flat global keys ('menu_brands', 'catalog_menu', ...). Against the
# project's FileBasedCache that means a test run both reads stale developer
# entries — categories with empty slugs, so {% url 'category_detail' %} raises
# NoReverseMatch — and writes fixtures into the running dev site's cache.
ISOLATED_CACHE = override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'store-tests',
    }
})


@ISOLATED_CACHE
class SearchApiTests(TestCase):
    """``/api/search/`` speaks the same contract as ``/api/catalog/``.

    The endpoint grew server-side sorting and paging to stop shipping the whole
    match set to the browser. These tests pin the parts that are easy to break
    quietly: the response shape, page coverage, the sort allowlist, and the
    boundary handling that keeps a hand-crafted query from erroring out.
    """

    _sku = 1000

    def setUp(self):
        cache.clear()

    @classmethod
    def setUpTestData(cls):
        # Only Product.save() slugifies its title; these models need it spelled
        # out, otherwise the API URLs come out as /api/catalog///.
        cls.main_category = MainCategory.objects.create(
            title='Пневмоинструмент', slug='pnevmoinstrument', ordering=1)
        cls.category = Category.objects.create(
            title='Гайковерты', slug='gajkoverty', main_category=cls.main_category, ordering=1)
        cls.brand = Brand.objects.create(
            title='TestBrand', slug='testbrand', ordering=1)

        # Deliberately mixed prices: three «по запросу» rows share price 0,
        # which is the case that used to make rows swap between pages.
        # Note Product.save() derives `price` from `price_wo_tax`, so the tests
        # seed the base price and read the resulting `price` back off the object.
        cls.priced = [
            cls._product('Гайковерт %d' % i, price_wo_tax)
            for i, price_wo_tax in enumerate([300, 100, 200, 50])
        ]
        cls.on_request = [cls._product('Товар по запросу %d' % i, 0) for i in range(3)]
        cls.unrelated = cls._product('Совсем другой инструмент', 999)

    @classmethod
    def _product(cls, title, price_wo_tax):
        cls._sku += 1
        return Product.objects.create(
            title=title,
            sku=cls._sku,
            price_wo_tax=price_wo_tax,
            category=cls.category,
            brand=cls.brand,
            is_visible=True,
        )

    def api(self, **params):
        response = self.client.get('/api/search/', {'query': 'Гайковерт', **params})
        self.assertEqual(response.status_code, 200)
        return response.json()

    def all_ids(self, **params):
        """Walk every page and return the ids in the order the UI would show."""
        first = self.api(perPage=2, **params)
        ids = [p['id'] for p in first['products']]
        for page in range(2, first['totalPages'] + 1):
            ids += [p['id'] for p in self.api(perPage=2, page=page, **params)['products']]
        return ids

    def test_response_contract(self):
        """The template reads exactly these four keys."""
        self.assertEqual(
            set(self.api().keys()),
            {'products', 'currentPage', 'totalPages', 'totalProducts'},
        )

    def test_total_counts_every_match_not_one_page(self):
        data = self.api(perPage=2)
        self.assertEqual(data['totalProducts'], len(self.priced))
        self.assertEqual(data['totalPages'], 2)
        self.assertEqual(data['currentPage'], 1)

    def test_pages_cover_every_product_exactly_once(self):
        ids = self.all_ids()
        self.assertEqual(len(ids), len(set(ids)), 'product repeated across pages')
        self.assertEqual(set(ids), {p.id for p in self.priced})

    def test_price_zero_is_reported_as_null(self):
        """«По запросу» reaches the client as null, which the card renders as text."""
        response = self.client.get('/api/search/', {'query': 'по запросу'})
        prices = {p['price'] for p in response.json()['products']}
        self.assertEqual(prices, {None})

    def test_sort_by_title(self):
        asc = [p['title'] for p in self.api(sortField='title', sortOrder='asc')['products']]
        desc = [p['title'] for p in self.api(sortField='title', sortOrder='desc')['products']]
        self.assertEqual(asc, sorted(asc))
        self.assertEqual(desc, sorted(asc, reverse=True))

    def test_sort_by_price_ignores_nulls(self):
        for order, reverse in (('asc', False), ('desc', True)):
            data = self.api(perPage=50, sortField='price', sortOrder=order)
            values = [p['price'] for p in data['products'] if p['price'] is not None]
            self.assertEqual(values, sorted(values, reverse=reverse))

    def test_rows_sharing_a_sort_value_keep_a_stable_order(self):
        """Nine «по запросу» rows all have price 0; without the id tiebreaker
        SQLite is free to return them in any order on each page."""
        first = self.all_ids(sortField='price', sortOrder='asc')
        second = self.all_ids(sortField='price', sortOrder='asc')
        self.assertEqual(first, second)

    def test_disallowed_sort_field_falls_back(self):
        for hostile in ['; DROP TABLE store_product', 'price; --', 'unknown_column', '']:
            data = self.api(sortField=hostile)
            self.assertEqual(data['totalProducts'], len(self.priced))

    def test_sort_order_is_validated(self):
        """Only an exact 'desc' reverses the listing; everything else ascends."""
        asc = [p['id'] for p in self.api(sortField='title', sortOrder='asc')['products']]
        desc = [p['id'] for p in self.api(sortField='title', sortOrder='desc')['products']]
        self.assertEqual(sorted(asc), sorted(desc), 'desc is not the reverse of asc')
        self.assertNotEqual(asc, desc, 'desc did not reverse anything')
        for hostile in ['DESC', 'desc; DROP TABLE', '1', '']:
            self.assertEqual(
                [p['id'] for p in self.api(sortField='title', sortOrder=hostile)['products']],
                asc,
                'sortOrder=%r was not normalised to asc' % hostile,
            )

    def test_fetch_url_percent_encodes_the_query(self):
        """The Vue fetch URL must not be broken by a query containing & or #.

        ``{{ query|urlencode }}`` is the only thing keeping «гайковерт & пневмо»
        from splitting into a second parameter — and dropping the filter is a
        silent break, since the page still renders and the API still answers.
        """
        html = self.client.get(
            '/search/', {'query': 'Гайковерт & пневмо'}).content.decode()
        self.assertIn('query=%D0%93%D0%B0%D0%B9%D0%BA%D0%BE%D0%B2%D0%B5%D1%80%D1%82', html)
        self.assertNotIn('/api/search/?query=Гайковерт &', html)

    def test_header_shows_the_lowest_priced_match(self):
        """«Цены от» in the results header, ignoring «по запросу» rows.

        price 0 means «по запросу», so letting it into the minimum would claim
        the search starts at 0 ₽. The on-request row is created here rather than
        in the fixture because it has to match the query too — the shared
        fixtures title those rows «Товар по запросу N», which a search for
        «Гайковерт» never returns.
        """
        Product.objects.create(
            title='Гайковерт по запросу', sku=9001, price_wo_tax=0,
            category=self.category, brand=self.brand, is_visible=True)

        html = self.client.get('/search/', {'query': 'Гайковерт'}).content.decode()
        cheapest = min(p.price for p in self.priced)
        rendered = '{:,.2f}'.format(cheapest).replace(',', ' ').replace('.', ',')
        self.assertIn('Цены от', html)
        self.assertIn(rendered, html)
        self.assertNotIn('0,00', html.split('Цены от')[1][:60])

    def test_per_page_falls_back_when_out_of_bounds(self):
        for hostile in [0, -5, 9999, 'abc', '']:
            data = self.api(perPage=hostile)
            self.assertEqual(len(data['products']), len(self.priced))

    def test_page_beyond_the_end_returns_the_last_page(self):
        data = self.api(perPage=2, page=9999)
        self.assertEqual(data['currentPage'], data['totalPages'])

    def test_non_integer_page_returns_the_first_page(self):
        self.assertEqual(self.api(page='abc')['currentPage'], 1)

    def test_page_count_matches_total_and_per_page(self):
        for per_page in [1, 2, 3, 4, 10]:
            data = self.api(perPage=per_page)
            self.assertEqual(data['totalPages'], -(-len(self.priced) // per_page))

    def test_no_match_returns_an_empty_but_valid_contract(self):
        response = self.client.get('/api/search/', {'query': 'нетакого'})
        data = response.json()
        self.assertEqual(data['products'], [])
        self.assertEqual(data['totalProducts'], 0)

    def test_empty_query_returns_the_same_shape(self):
        """The template always reads the same keys, including on an empty query."""
        response = self.client.get('/api/search/', headers={'x-requested-with': 'XMLHttpRequest'})
        self.assertEqual(
            set(response.json().keys()),
            {'products', 'currentPage', 'totalPages', 'totalProducts'},
        )

    def test_invisible_products_are_excluded(self):
        Product.objects.filter(title__startswith='Гайковерт').update(is_visible=False)
        self.assertEqual(self.api()['totalProducts'], 0)

    def test_ordering_ends_on_a_unique_column(self):
        """Pin the tiebreaker on the SQL the listing queries actually run.

        A page-coverage test cannot catch a missing one: SQLite is free to
        return rows sharing a sort value in any order, and on this data it
        hands back the same order every time, so the behavioural tests pass with
        the tiebreaker deleted. Only the invariant — ORDER BY closes on a unique
        column — is deterministic enough to assert.

        The filter looks for the requested sort column rather than any product
        query: context processors run their own unordered-listing queries, which
        carry no LIMIT and so need no tiebreaker.
        """
        endpoints = {
            'search': ('/api/search/', {'query': 'Гайковерт'}),
            'category': ('/api/catalog/%s/%s/' % (self.main_category.slug, self.category.slug), {}),
            'brand': ('/api/brands/%s/' % self.brand.slug, {}),
        }
        for name, (url, extra) in endpoints.items():
            for sort_order in ('asc', 'desc'):
                with CaptureQueriesContext(connection) as captured:
                    self.client.get(url, {**extra, 'sortField': 'price', 'sortOrder': sort_order})
                listings = [
                    q['sql'] for q in captured.captured_queries
                    if 'FROM "store_product"' in q['sql']
                    and re.search(r'ORDER BY\b[^;]*"price"', q['sql'])
                ]
                self.assertEqual(len(listings), 1,
                                 '%s/%s: expected one price-ordered listing, got %d'
                                 % (name, sort_order, len(listings)))
                order_by = listings[0].rsplit('ORDER BY', 1)[1].split('LIMIT')[0]
                self.assertTrue(
                    re.search(r'\bid\b', order_by),
                    '%s/%s: ORDER BY does not close on the primary key -> %s'
                    % (name, sort_order, order_by),
                )

    def test_page_view_count_matches_the_api(self):
        """The header renders the SSR count first; if the two disagreed the
        number would visibly change once the client finished loading."""
        page = self.client.get('/search/', {'query': 'Гайковерт'})
        self.assertEqual(page.context['count'], self.api()['totalProducts'])
        self.assertIn('totalProducts: %d' % page.context['count'],
                      page.content.decode())


@ISOLATED_CACHE
class SearchPageMetaTests(TestCase):
    """Search pages must stay out of the index."""

    def setUp(self):
        cache.clear()

    @classmethod
    def setUpTestData(cls):
        main_category = MainCategory.objects.create(
            title='Пневмоинструмент', slug='pnevmoinstrument', ordering=1)
        category = Category.objects.create(
            title='Гайковерты', slug='gajkoverty', main_category=main_category, ordering=1)
        Product.objects.create(title='Гайковерт 5', sku=900,
                               price_wo_tax=100, category=category, is_visible=True)

    def test_search_page_is_noindex(self):
        html = self.client.get('/search/', {'query': 'Гайковерт'}).content.decode()
        self.assertIn('<meta name="robots" content="noindex, follow" />', html)

    def test_catalogue_pages_stay_indexable(self):
        """The robots block defaults to index, follow — a regression guard on
        the shared base template."""
        html = self.client.get('/').content.decode()
        self.assertIn('<meta name="robots" content="index, follow" />', html)

    def test_description_mentions_the_query(self):
        html = self.client.get('/search/', {'query': 'Гайковерт'}).content.decode()
        self.assertIn('Гайковерт', html.split('name="description"')[1][:200])

    def test_robots_txt_does_not_block_search(self):
        """A Disallow would stop the crawler before it could read noindex."""
        robots = self.client.get('/robots.txt').content.decode()
        directives = [line.strip() for line in robots.splitlines()
                      if line.strip() and not line.strip().startswith('#')]
        self.assertNotIn('Disallow: /search/', directives)
