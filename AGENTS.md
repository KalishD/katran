# Katran E-Commerce

Django 5.2 e-commerce site for pneumatic tools (Russian market: katran-pnevmo.ru).

## Quick Start

```bash
# Activate venv
source venvkatran/bin/activate   # Linux/Mac
.\env\Scripts\activate           # Windows (env/ also exists)

# Run dev server
python manage.py runserver
```

**Tests:** `apps/store/tests.py` holds the only suite (search API + search-page SEO). No linter, formatter, or CI/CD is configured.

```bash
# NB: `manage.py test apps.store` fails with
# `_getfullpathname: path should be string, bytes or os.PathLike, not NoneType`
# because `apps` is a namespace package with no __init__.py. Address the module:
& ".\env\Scripts\python.exe" manage.py test apps.store.tests
```

## Architecture

```
katran/          → Django project config (settings, urls, wsgi, sitemaps)
apps/
  store/         → Products, categories, brands, variables, patents (main models + admin CSV import)
  cart/          → Session-based cart (apps/cart/cart.py)
  comparison/    → Session-based product comparison (max 4 items)
  order/         → Orders, checkout, email notifications
  blog/          → Posts with linked products
  core/          → Frontpage, static pages, middleware, templatetags, CSP report endpoint
static/          → CSS, JS, images, admin assets
media/           → User-uploaded content (products, brands, posts, patents)
```

**Root `store/` directory** exists alongside `apps/store/` — it contains an older `admin.py` backup. Ignore it.

## Key Facts

- **Database**: SQLite in dev (`db.sqlite3`). Production uses MySQL/PostgreSQL (both drivers in requirements.txt).
- **Settings**: `katran/settings.py` is gitignored (see `.gitignore`). The committed version has DEBUG=True, SECRET_KEY exposed.
- **Locale**: `LANGUAGE_CODE = 'ru-RU'`, date format `d E Y`.
- **Cart**: Session-based (`CART_SESSION_ID = 'cart'`), 24h cookie lifetime.
- **Comparison**: Session-based (`COMPARISON_SESSION_ID = 'comparison'`), max 4 items.
- **Tax**: Product tax is hardcoded at 22% (`Product.tax = 22`). Price auto-calculated from `price_wo_tax`.
- **Slugs**: Auto-generated from title via `python-slugify` on product save.
- **Images**: Pillow auto-converts to RGB/JPEG and creates 60x60 thumbnails on save.
- **Rich text**: django-summernote for blog/product descriptions.
- **SEO**: Schema.org product metadata via `django-meta`. Multiple sitemaps (XML + HTML).
- **API**: JSON endpoints at `/api/` for cart operations, comparison, category products, search (no auth required).
- **Emails**: Order confirmations sent to `office@katran-pnevmo.ru` and to customer.
- **Rate limiting**: Checkout is rate-limited to 5 attempts per hour per session.

## Frontend

Category/brand product listings use Vue.js fetching from API endpoints (`category_products_api`, `brand_products_api`, `search_api`). Templates use `django_summernote` for admin editing. Design system documented in `DESIGN.md`.

## Gotchas

- **Listing queries must end on a unique column.** `price` is 0 for every «по запросу» row and `ordering` repeats heavily, so `ORDER BY price` alone lets rows swap between pages — the same product twice on one listing, missing from another. `sorted_products()` in `apps/store/views.py` appends the primary key; keep that last. A page-coverage test cannot catch a missing tiebreaker (SQLite returns the same order regardless), so `test_ordering_ends_on_a_unique_column` asserts on the SQL via `CaptureQueriesContext`.
- **The nav/menu context processors cache under flat global keys** (`menu_brands`, `catalog_menu`, `menu_categories`, `all_products_ids`, …) in the project's `FileBasedCache`. A test run therefore both reads developer cache entries and writes fixtures into the dev site's cache. Test classes override `CACHES` with `locmem` and clear it in `setUp`.
- **`thumbnail.url` on an empty field raises, it does not render blank.** `base.html` (brand menu) and `category_detail_list.html` guard with `{% if ... %}`; without that a single brand or product lacking an image makes *every* page 500.
- **«По запросу» = `price == 0`.** There is no dedicated flag on `Product` — neither in the admin nor in templates. Everything keys off `price == 0`.
- **`PriceRequest` exists but is NOT wired up.** On-request products go through the ordinary `add_to_cart` flow; the cart doubles as the price-request channel because no payment gateway is integrated. Kept as a ready-but-unused scaffold (**do not delete**):
  - model `apps/store/models.py::PriceRequest` + migration `store.0003_pricerequest`, `PriceRequestQuerySet.pending()`, `PriceRequestAdmin`, `send_office_email()`
  - endpoint `apps/store/api.py::api_request_price` + `rate_limit_price_request` + `PRICE_REQUEST_RATE_LIMIT/WINDOW` — still functional, but no UI calls it
  - email template `apps/store/templates/emails/price_request.html`
  - the modal markup in `apps/store/templates/product_detail.html` plus Vue methods `openPriceRequest`/`closePriceRequest`/`requestPrice` and data fields `priceModal`/`priceForm`/`priceSent`/`priceError`/`priceRequestId`

  There are **zero** call sites for `openPriceRequest()`. To restore the standalone request form, call `openPriceRequest()` from the product page button.
- `apps.core.middleware.WwwRedirectMiddleware` is registered but currently a no-op (pass-through).
- CSP middleware is configured (`csp.middleware.CSPMiddleware`) — watch for CSP violations in dev.
- `settings.py` contains `SECRET_KEY` in plaintext — never commit real production settings.
- The `STATICFILES_DIRS` path construction uses `Path(__file__).parent.joinpath(BASE_DIR, 'static')` which may behave unexpectedly.
- Migration files are zipped in some app directories (`migrations.rar`) — don't delete without checking.
- The `runserver` script at root is a Linux bash script (`source venvkatran/bin/activate`), not Windows-compatible.
- `apps/_admin_unused.py` is a stale backup of `apps/store/admin.py` — do not edit or import from it.
