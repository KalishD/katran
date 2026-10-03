from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F, Value
from django.db.models.functions import Coalesce, Lower
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_page, never_cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
from django.contrib.postgres.aggregates import StringAgg
from django.contrib.postgres.search import TrigramSimilarity

from .models import Product, Category, Brand, Variable, VariableItem, MainCategory, Patent

from django.db.models import Count
from django.db.models import Avg, Max, Min, Sum
import re

def spec_payload(product):
    """Compressor-relevant specs for listing cards, keyed by stable spec slug.

    Surfacing air consumption / pressure / inlet next to the price is the
    main thing competitors do not do, and it is the first question a buyer
    of a pneumatic tool has.

    ``spec_rows`` is the pre-ordered, pre-labelled, length-capped version of
    the same data. The Vue card renders it directly instead of re-deriving the
    priority and the unit wording, which is what kept the two render paths in
    sync.
    """
    return {
        slug: spec['text']
        for slug, spec in product.get_specs().items()
    } | {'spec_rows': product.get_spec_rows()}


def category_seo_context(category, products_qs):
    """Per-category copy numbers for the SEO block at the bottom of the page.

    Everything here is derived from live catalog data, so the text differs
    between categories instead of being one boilerplate paragraph.
    """
    visible = list(
        products_qs.filter(is_visible=True)
        .select_related('brand')
        .prefetch_related('variable_set__varitem')
    )
    priced = [p for p in visible if p.price]

    spec_values = {}
    for product in visible:
        for slug, spec in product.get_specs().items():
            spec_values.setdefault(slug, []).append(spec['value'])

    def _sortable(slug):
        out = []
        for value in spec_values.get(slug, []):
            raw = str(value).replace(',', '.').replace(' ', '')
            try:
                out.append(float(raw))
            except ValueError:
                pass
        return sorted(out)

    discs = _sortable('disc')
    consumption = _sortable('air_consumption')

    brands = sorted({p.brand.title for p in visible if p.brand})
    pressures = sorted({str(v) for v in spec_values.get('air_pressure', []) if v})

    # МПа -> бар (1 МПа = 10 бар), formatted the Russian way, so the copy never
    # states a bar figure that contradicts the pressure in the catalog.
    pressure_bar = None
    if pressures:
        try:
            pressure_bar = '{},{}'.format(
                *('{:.1f}'.format(float(pressures[0].replace(',', '.')) * 10).split('.'))
            )
        except ValueError:
            pressure_bar = None

    return {
        'count': len(visible),
        'brand_list': brands,
        'price_min': min((p.price for p in priced), default=None),
        'price_max': max((p.price for p in priced), default=None),
        'has_priced': bool(priced),
        'on_request_count': len(visible) - len(priced),
        'disc_min': int(discs[0]) if discs else None,
        'disc_max': int(discs[-1]) if discs else None,
        'air_min': int(consumption[0]) if consumption else None,
        'air_max': int(consumption[-1]) if consumption else None,
        'pressure_label': ' и '.join(pressures) if pressures else None,
        'pressure_bar': pressure_bar,
    }

def plural(n):
    """Russian count noun: 1 товар / 2 товара / 5 товаров."""
    n10, n100 = n % 10, n % 100
    if n10 == 1 and n100 != 11:
        return 'товар'
    if 2 <= n10 <= 4 and not (12 <= n100 <= 14):
        return 'товара'
    return 'товаров'


def sorted_products(products_qs, request, allowed_fields, default_field, tiebreakers=('id',)):
    """Apply ``?sortField``/``?sortOrder`` to a product queryset.

    The ordering has to end on a unique column. ``price`` is 0 for every
    «по запросу» product and ``ordering`` repeats heavily, so rows sharing a
    sort value could otherwise swap between pages — the same product appearing
    twice on one listing and missing from another. ``tiebreakers`` defaults to
    the primary key; pass extra columns before it to keep an intentional
    grouping (the category listing groups by category).
    """
    sort_field = request.GET.get('sortField', default_field)
    sort_order = request.GET.get('sortOrder', 'asc')

    if sort_field not in allowed_fields:
        sort_field = default_field

    # Only an exact 'desc' flips the direction, so any other value — 'DESC',
    # 'desc; DROP TABLE', '' — lands on ascending without a separate allowlist.
    prefix = '-' if sort_order == 'desc' else ''
    return products_qs.order_by(f'{prefix}{sort_field}', *tiebreakers)


def search_queryset(raw_query):
    """Single source of truth for «what does this query match».

    The page view and the JSON API used to disagree: the view matched the whole
    string as one term, the API split it into words and ANDed them. The count in
    the header therefore changed once the client finished loading. Both go
    through here now so they cannot drift apart again.
    """
    q_objects = Q()
    for term in raw_query.split():
        q_objects |= (
            Q(title__icontains=term) |
            Q(description__icontains=term) |
            Q(article__icontains=term)
        )

    return (
        Product.objects.filter(is_visible=True)
        .filter(q_objects)
        .distinct()
        .select_related('brand', 'category__main_category')
        .prefetch_related('variable_set__varitem')
    )


@never_cache
def search(request):
    raw_query = request.GET.get('query')

    if not raw_query:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'products_html': ''})
        return redirect('frontpage')

    query = raw_query

    products_list = search_queryset(raw_query)
    total = products_list.count()

    # «Цены от» for the results header. Aggregated in SQL rather than in Python
    # so the whole match set is never pulled into memory; price 0 means
    # «по запросу» and must not win the minimum.
    price_min = products_list.filter(price__gt=0).aggregate(value=Min('price'))['value']

    context = {
        'query': query,
        'raw_query': raw_query,
        'products': products_list,
        'total': total,
        'price_min': price_min,
        # Description used to be the same constant string on every search page.
        # Naming the query and the hit count makes it both unique and truthful.
        'count': total,
        'keywords': f'{raw_query} заказ с доставкой по всей России, доставка ТК',
        'description': (
            f'Найдено {total} {plural(total)} по запросу «{raw_query}» — пневматический '
            f'инструмент в наличии и под заказ в интернет-магазине Катран-Пневмо.'
        ),
    }
    return render(request, 'search.html', context)

@never_cache
@require_GET
def search_api(request):
    """Search results with the same contract as ``category_products_api``.

    The template used to pull the whole match set and sort it in the browser,
    which meant a broad query shipped every product in the response. Sorting
    and paging happen here now, so the payload stays one page wide.
    """
    raw_query = request.GET.get('query')
    if not raw_query:
        empty = {'products': [], 'currentPage': 1, 'totalPages': 0, 'totalProducts': 0}
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(empty)
        return render(request, 'search.html', {'query': raw_query, 'products': [], 'keywords': ''})

    products_qs = search_queryset(raw_query)
    products_qs = sorted_products(products_qs, request, ALLOWED_SORT_FIELDS_SEARCH, 'ordering')

    page = request.GET.get('page', 1)
    per_page = request.GET.get('perPage', 15)
    try:
        per_page = int(per_page)
        if not (1 <= per_page <= 100):
            per_page = 15
    except ValueError:
        per_page = 15

    paginator = Paginator(products_qs, per_page)
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    products = []
    for p in products_page.object_list:

        products.append({
            'id': p.id,
            'title': p.title,
            'price': float(p.price) if p.price else None,
            'image': p.image.url if p.image else '',
            'image_sm': p.get_resized_url('image', 'sm') if p.image else '',
            'image_md': p.get_resized_url('image', 'md') if p.image else '',
            'srcset': p.get_srcset('image') if p.image else '',
            'category': p.category.title,
            'main_category': p.category.main_category.title,
            'category_url': p.category.get_absolute_url(),
            'main_category_url': p.category.main_category.get_absolute_url(),
            'brand': p.brand.title if p.brand else None,
            'brand_url': p.brand.get_absolute_url() if p.brand else None,
            'brand_image': p.brand.image.url if p.brand and p.brand.image else None,
            'url': p.get_absolute_url(),
            'in_stock': p.in_stock,
            'specs': spec_payload(p),
            })

    return JsonResponse({
        'products': products,
        'currentPage': products_page.number,
        'totalPages': paginator.num_pages,
        'totalProducts': paginator.count,
    })

@cache_page(60 * 30)  # 30 minutes
def catalog(request):
    categories = Category.objects.select_related('main_category').all()
    keywords = 'Заказать пневматический инструмент, каталог пневмоинструмента'
    description = 'Каталог пневмоинструмента на сайте katran-pnevmo.ru'
    context = {
        'categories': categories,
        'keywords': keywords,
        'description': description,
        }

    return render(request, 'catalog.html', context)

@cache_page(60 * 30)  # 30 minutes
def main_category_detail(request, slug):
    main_category = get_object_or_404(MainCategory, slug=slug)
    categories = main_category.get_categories().select_related('main_category')
    keywords = f'Заказать {main_category.title}, купить {main_category.title}'
    description = f'Заказать {main_category.title} '
    context = {
        'main_category': main_category, 
        'categories': categories,
        'keywords': keywords,
        'description': description, 
        }
    return render(request, 'main_category_detail.html', context)






@cache_page(60 * 15)  # 15 minutes
def category_detail(request, maincategory_slug, slug):
    """
    Renders the category detail page.
    This view primarily fetches the category details and passes them to the template.
    Product data is now fetched dynamically via the category_products_api.
    """
    category = get_object_or_404(Category, slug=slug, main_category__slug=maincategory_slug)

    # Optimized: fetch variable IDs with a single query instead of loading all products
    from django.db.models import Subquery, OuterRef
    all_cat_vars_ids = Variable.objects.filter(
        product__category=category
    ).values('varitem_id').distinct().values_list('varitem_id', flat=True)
    all_cat_vars = VariableItem.objects.filter(id__in=list(all_cat_vars_ids))
    # These context variables might still be useful for initial rendering of category-specific headers
    # or static elements that don't change with pagination/sorting.
    # If `var_titles` and `all_cat_vars` are needed for dynamic product characteristics,
    # they should ideally be fetched and included in the JSON response of `category_products_api`
    # or handled entirely on the frontend if they are truly static for the category.
    # For now, they are commented out as they are not directly used by the Vue app's product loop.
    # var_titles = []
    # first_product_vars = category.products.all().annotate(count=Count('variables')).latest('count').variable_set.all()
    # all_cat_vars = VariableItem.objects.filter(id__in=list(category.products.all().order_by('variables').values_list('variables', flat=True).distinct()))

    keywords = f'Заказать {category.title}'
    description = f'Заказать {category.title}'
    if category.description:
        clean_desc = ' '.join(re.sub(r'<[^>]+>', ' ', category.description).split())
        if len(clean_desc) > 60:
            description = clean_desc[:170].rsplit(' ', 1)[0] + '…'
            keywords = f'купить {category.title}, {category.title}, {category.main_category.title}'

    # SSR-данные для роботов/режима без JS. Порядок совпадает с дефолтной сортировкой Vue-сетки.
    # prefetch обязателен: карточка рендерит get_specs(), иначе будет N+1 на каждый товар.
    category_qs = (
        Product.objects.filter(category=category, is_visible=True)
        .select_related('brand')
        .prefetch_related('variable_set__varitem')
    )
    seo = category_seo_context(category, Product.objects.filter(category=category))
    products = list(category_qs.order_by('ordering'))
    products_total = len(products)
    products = products[:20]

    context = {
        'category': category,
        # 'products': products, # Products are now fetched via API
        # 'var_titles': first_product_vars,
        'all_cat_vars': all_cat_vars,
        'products': products,
        'products_total': products_total,
        'keywords': keywords,
        'description': description,
        'seo': seo,
    }
    return render(request, 'category_detail.html', context)


ALLOWED_SORT_FIELDS_CATEGORY = {'is_features', 'title', 'price', 'price_wo_tax', 'sku', 'ordering', 'created_at'}

# Поиск сортируется только по тому, что реально предлагает его панель.
ALLOWED_SORT_FIELDS_SEARCH = {'ordering', 'title', 'price'}

@never_cache
@require_GET
def category_products_api(request, main_category_slug, category_slug):
    """
    API endpoint to fetch products for a category with pagination and sorting.
    """
    category = get_object_or_404(Category, slug=category_slug, main_category__slug=main_category_slug)
    products_qs = Product.objects.filter(category=category, is_visible=True).select_related('brand', 'category__main_category').prefetch_related('variable_set__varitem')

    products_qs = sorted_products(products_qs, request, ALLOWED_SORT_FIELDS_CATEGORY, 'is_features',
                                  tiebreakers=('category', 'id'))

    # Get pagination parameters from request.GET
    page = request.GET.get('page', 1)
    per_page = request.GET.get('perPage', 15) # Default items per page

    # Validate and sanitize per_page
    try:
        per_page = int(per_page)
        if not (1 <= per_page <= 100): # Set a reasonable limit to prevent excessively large pages
            per_page = 15
    except ValueError:
        per_page = 15 # Fallback to default if not a valid integer

    # Initialize Paginator
    paginator = Paginator(products_qs, per_page)

    # Get the requested page
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products_page = paginator.page(paginator.num_pages)

    # Get all unique variable items for the category's products for consistent characteristics display.
    # Use the same optimized query as category_detail
    all_cat_vars_ids = Variable.objects.filter(
        product__category=category
    ).values('varitem_id').distinct().values_list('varitem_id', flat=True)
    all_cat_vars = VariableItem.objects.filter(id__in=list(all_cat_vars_ids))

    products_data = []
    for p in products_page.object_list: # Iterate over products for the current page
        # Collect variables for the current product — single iteration, not triple
        variables = {}
        for v in p.variable_set.all():
            variables[v.varitem] = {
                'value': v.value,
                'title': v.varitem.title,
                'dimention': v.varitem.dimention,
            }

        characteristics = []
        characteristicsitems = []
        characteristicsdimention = []

        # Populate characteristics based on all_cat_vars for consistent structure
        for var in all_cat_vars:
            var_data = variables.get(var)
            characteristics.append(var_data['value'] if var_data else None)
            characteristicsitems.append(var_data['title'] if var_data else None)
            characteristicsdimention.append(var_data['dimention'] if var_data else None)

        products_data.append({
            'id': p.id,
            'title': p.title,
            'price': float(p.price) if p.price else None,
'image': p.image.url if p.image else '',
            'image_sm': p.get_resized_url('image', 'sm') if p.image else '',
            'image_md': p.get_resized_url('image', 'md') if p.image else '',
            'srcset': p.get_srcset('image') if p.image else '',
            'category': p.category.title,
            'main_category': p.category.main_category.title,
            'category_url': p.category.get_absolute_url(),
            'main_category_url': p.category.main_category.get_absolute_url(),
            'brand': p.brand.title if p.brand else None,
            'brand_url': p.brand.get_absolute_url() if p.brand else None,
            'brand_image': p.brand.image.url if p.brand and p.brand.image else None,
            'url': p.get_absolute_url(),
            'characteristics': characteristics,
            'characteristicsitems': characteristicsitems,
            'characteristicsdimention': characteristicsdimention,
            'is_features': p.is_features,
            'sku': p.sku,
            'in_stock': p.in_stock,
            'specs': spec_payload(p),
        })

    return JsonResponse({
        'products': products_data,
        'currentPage': products_page.number,
        'totalPages': paginator.num_pages,
        'totalProducts': paginator.count,
    })

@cache_page(60 * 30)  # 30 minutes
def product_detail(request, maincategory_slug, category_slug, slug):
    product = get_object_or_404(
        Product.objects.select_related(
            'category__main_category', 'brand', 'analog', 'analog__brand', 'analog__category__main_category'
        ).prefetch_related(
            'variable_set__varitem', 'faqs', 'parts', 'similar_products'
        ),
        slug=slug
    )
    category = product.category
    variables = product.variable_set.all().order_by('-varitem__is_primary')
    variables_list = ''
    for var in variables:
        if var.varitem.is_primary:
            variables_list += var.value + (var.varitem.dimention if var.varitem.dimention else '') + '; '
    cln_title = re.sub(r'\s*\([^()]*\)$', '', product.title)
    keywords = 'купить '\
                + cln_title\
                + ', '\
                + str(product.keywords)
    
    meta_description = f'{cln_title} {product.brand} с доставкой по всей России; {variables_list}'
    if product.price:
        brand_name = product.brand.title if product.brand else ''
        head = f'{cln_title} — {brand_name}'.strip(' —')
        meta_description = (
            f'{head}, {product.price:.0f} ₽ с НДС 22%. '
            f'{category.title.lower()}: в наличии на складе в СПб, отгрузка по РФ и СНГ, '
            f'гарантия 12 месяцев, поможем подобрать диск и аналог.'
        )
    if len(meta_description) > 158:
        meta_description = meta_description[:157].rsplit(' ', 1)[0] + '…'
    # Создание и передача объекта meta в контекст
    meta = product.as_meta(request)

    context = {
        'cln_title': cln_title,
        'variables_list': variables_list,
        'product': product, 
        'category': category, 
        'variables': variables, 
        'keywords': keywords,
        'description': meta_description,
        'meta': meta,
        }

    return render(request, 'product_detail.html', context)





@cache_page(60 * 30)  # 30 minutes
def brands(request):
    keywords = 'Каталог производителей пневмоинструмент'
    description = 'Каталог производителей пневмоинструмент'

    brands_qs = Brand.objects.all().order_by('ordering')
    all_products = Product.objects.filter(
        is_visible=True,
        category__main_category__in=range(1, 2)
    ).select_related('brand', 'category__main_category').order_by('?')

    brand_product_map = {}
    for p in all_products:
        if p.brand_id not in brand_product_map:
            brand_product_map[p.brand_id] = []
        if len(brand_product_map[p.brand_id]) < 5:
            brand_product_map[p.brand_id].append(p)

    brand_items = []
    for brand in brands_qs:
        brand_items.append({
            'brand': brand,
            'products': brand_product_map.get(brand.id, [])
        })

    context = {
        'brand_items': brand_items,
        'keywords': keywords,
        'description': description,
    }
    return render(request, 'brands.html', context)

@cache_page(60 * 30)  # 30 minutes
def brand_detail(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    products = brand.products.filter(is_visible=True).select_related(
        'category__main_category'
    ).order_by("is_features")
    keywords = f'Заказать пневмоинструмент фирмы {brand.title}, купить {brand.title}, заказать {brand.title}, пневмоинструмент {brand.title}'
    description = f'Заказать пневмоинструмент фирмы {brand.title} с доставкой по всей России'
    all_brand_vars = VariableItem.objects.filter(id__in=list(brand.products.all().order_by('variables').values_list('variables', flat=True).distinct()))
    context = {
        'brand': brand,
        'products': products,
        'keywords': keywords,
        'description': description,
        'all_brand_vars': all_brand_vars,
    }

    return render(request, 'brand_detail.html', context)


ALLOWED_SORT_FIELDS_BRAND = {'category__ordering', 'title', 'price', 'price_wo_tax', 'sku', 'ordering', 'created_at'}

@never_cache
@require_GET
def brand_products_api(request, slug):
    brand = get_object_or_404(Brand, slug=slug)
    """
    API endpoint to fetch products for a category with pagination and sorting.
    """
    products_qs = Product.objects.filter(brand=brand, is_visible=True).select_related('brand', 'category__main_category').prefetch_related('variable_set__varitem')

    products_qs = sorted_products(products_qs, request, ALLOWED_SORT_FIELDS_BRAND, 'category__ordering')

    # Get pagination parameters from request.GET
    page = request.GET.get('page', 1)
    per_page = request.GET.get('perPage', 20) # Default items per page

    # Validate and sanitize per_page
    try:
        per_page = int(per_page)
        if not (1 <= per_page <= 100): # Set a reasonable limit to prevent excessively large pages
            per_page = 20
    except ValueError:
        per_page = 20 # Fallback to default if not a valid integer

    # Initialize Paginator
    paginator = Paginator(products_qs, per_page)

    # Get the requested page
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products_page = paginator.page(paginator.num_pages)

    # Get all unique variable items for the brand's products for consistent characteristics display.
    all_brand_vars_ids = Variable.objects.filter(
        product__brand=brand
    ).values('varitem_id').distinct().values_list('varitem_id', flat=True)
    all_brand_vars = VariableItem.objects.filter(id__in=list(all_brand_vars_ids))

    products_data = []
    for p in products_page.object_list: # Iterate over products for the current page
        # Collect variables for the current product — single iteration, not triple
        variables = {}
        for v in p.variable_set.all():
            variables[v.varitem] = {
                'value': v.value,
                'title': v.varitem.title,
                'dimention': v.varitem.dimention,
            }

        characteristics = []
        characteristicsitems = []
        characteristicsdimention = []

        # Populate characteristics based on all_brand_vars for consistent structure
        for var in all_brand_vars:
            var_data = variables.get(var)
            characteristics.append(var_data['value'] if var_data else None)
            characteristicsitems.append(var_data['title'] if var_data else None)
            characteristicsdimention.append(var_data['dimention'] if var_data else None)

        products_data.append({
            'id': p.id,
            'title': p.title,
            'price': float(p.price) if p.price else None,
            'image': p.image.url if p.image else '',
            'image_sm': p.get_resized_url('image', 'sm') if p.image else '',
            'image_md': p.get_resized_url('image', 'md') if p.image else '',
            'srcset': p.get_srcset('image') if p.image else '',
            'category': p.category.title,
            'main_category': p.category.main_category.title,
            'category_url': p.category.get_absolute_url(),
            'main_category_url': p.category.main_category.get_absolute_url(),
            'brand': p.brand.title if p.brand else None,
            'brand_url': p.brand.get_absolute_url() if p.brand else None,
            'brand_image': p.brand.image.url if p.brand and p.brand.image else None,
            'url': p.get_absolute_url(),
            'characteristics': characteristics,
            'characteristicsitems': characteristicsitems,
            'characteristicsdimention': characteristicsdimention,
            'is_features': p.is_features,
            'sku': p.sku,
            'in_stock': p.in_stock,
            'specs': spec_payload(p),
        })

    return JsonResponse({
        'products': products_data,
        'currentPage': products_page.number,
        'totalPages': paginator.num_pages,
        'totalProducts': paginator.count,
    })