---
name: django-audit
description: Run a security and code quality audit on the Django project, then fix issues by severity
---

# Django Audit (Katran)

## Quick audit checklist

Run through these checks in order. Fix Critical first, then High, Medium, Low.

### 1. Security

- **Secrets exposed**: Check `settings.py` for hardcoded SECRET_KEY, DEBUG=True, exposed API keys. Should use `os.environ.get()` with safe dev defaults.
- **XSS**: Search for `|safe` usage without sanitization. Check `productsstring`, template variables rendered with `|safe`. Use `json.dumps()` instead of `%` string formatting for JS data.
- **CSRF**: Check API views for `@csrf_exempt`. Verify cart/checkout forms have `{% csrf_token %}`.
- **Auth/rate-limit**: Check checkout API for rate limiting (should use Django cache).
- **File uploads**: Check Summernote upload restrictions and `/temp/` endpoint access.

```powershell
# Find |safe usage
grep -r "|safe" apps/*/templates/ --include="*.html"
# Find csrf_exempt
grep -r "csrf_exempt" apps/
# Find hardcoded secrets
grep -r "SECRET_KEY\|password\|api_key" katran/settings.py
```

### 2. Code quality

- **Duplicate code**: Check for near-clone admin files, duplicated utility functions.
- **Dead code**: Search for `print()` statements, unused imports, commented-out code.
- **Wrong paths**: Check `upload_to` values match the model (e.g., Category images in brands folder).
- **FK on_delete**: Check all ForeignKey fields for `on_delete=DO_NOTHING` — should be CASCADE, SET_NULL, or PROTECT.
- **Duplicate middleware**: Check MIDDLEWARE list for entries listed twice.

### 3. Data integrity

- **FloatField for money**: Price fields should be `DecimalField(10,2)`, not FloatField.
- **JSON serialization**: After DecimalField change, any `json.dumps()` or `JsonResponse` must convert via `float()` or `str()`.
- **Image processing**: Check Pillow `.convert('RGB')` return value is assigned (not discarded).

### 4. Performance

- **N+1 queries**: Check context processors and views for missing `select_related`/`prefetch_related`.
- **Missing indexes**: Check query patterns in Product/Category for commonly filtered fields.
- **Stale migrations**: Check for no-op migrations in migration chains.

### 5. SEO

- **Meta tags**: Check canonical URL, og:url, og:image, description on all page types.
- **Schema.org**: Verify structured data is page-specific (not same FAQPage on every page).
- **Breadcrumbs**: Verify BreadcrumbList reflects actual page hierarchy.
