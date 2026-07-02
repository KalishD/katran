# Katran E-Commerce

Django 5.2 e-commerce site for pneumatic tools (Russian market: katran-pnevmo.ru).

## Quick Start

```bash
# Activate venv
source venvkatran/bin/activate   # Linux/Mac
.\env\Scripts\activate           # Windows (env/ also exists)

# Run dev server
python manage.py runserver

# Common Django commands
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py shell
```

## Architecture

```
katran/          → Django project config (settings, urls, wsgi)
apps/
  store/         → Products, categories, brands, variables, patents (main models)
  cart/          → Session-based cart (apps/cart/cart.py)
  order/         → Orders, checkout, email notifications
  blog/          → Posts with linked products
  core/          → Frontpage, static pages, middleware, templatetags
```

## Key Facts

- **Database**: SQLite in dev (`db.sqlite3`). Production uses MySQL/PostgreSQL (both drivers in requirements.txt).
- **Settings**: `katran/settings.py` is gitignored. The committed version has DEBUG=True, SECRET_KEY exposed.
- **Locale**: `LANGUAGE_CODE = 'ru-RU'`, date format `d E Y`.
- **Cart**: Session-based (`CART_SESSION_ID = 'cart'`), 24h cookie lifetime.
- **Tax**: Product tax is hardcoded at 22% (`Product.tax = 22`). Price auto-calculated from `price_wo_tax`.
- **Slugs**: Auto-generated from title via `python-slugify` on product save.
- **Images**: Pillow auto-converts to RGB/JPEG and creates 60x60 thumbnails on save.
- **Rich text**: django-summernote for blog/product descriptions.
- **SEO**: Schema.org product metadata via `django-meta`. Multiple sitemaps (XML + HTML).
- **API**: JSON endpoints at `/api/` for cart operations, category products, search (no auth required).
- **Emails**: Order confirmations sent to `office@katran-pnevmo.ru` and to customer.

## Frontend

Category/brand product listings use Vue.js fetching from API endpoints (`category_products_api`, `brand_products_api`, `search_api`). Templates use `django_summernote` for admin editing.

## Gotchas

- `apps.core.middleware.WwwRedirectMiddleware` is registered but currently a no-op (pass-through).
- CSP middleware is configured (`csp.middleware.CSPMiddleware`) — watch for CSP violations in dev.
- `settings.py` contains `SECRET_KEY` in plaintext — never commit real production settings.
- The `STATICFILES_DIRS` path construction uses `Path(__file__).parent.joinpath(BASE_DIR, 'static')` which may behave unexpectedly.
- Migration files are zipped in some app directories (`migrations.rar`) — don't delete without checking.
