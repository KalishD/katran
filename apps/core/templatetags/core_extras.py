from django import template
register = template.Library()

@register.simple_tag
def plural_ru(count, one, few, many):
    # Русский требует 3 формы; встроенный pluralize в Django 5.2 принимает только 2 и молча
    # возвращает пустую строку, поэтому правило вынесено сюда.
    try:
        n = abs(int(count))
    except (TypeError, ValueError):
        return many
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many

@register.filter
def filter_by_main_category_id(categories, main_category_id):
    return [cat for cat in categories if cat.main_category.id == main_category_id]

@register.filter
def filter_products_by_category_id(products, category_id):
    return [prod for prod in products if prod.category.id == category_id]

@register.filter
def product_category_sort(products, order):
    filtered_prod = products.order_by(order)
    return filtered_prod

# Breadcrumb
@register.simple_tag
def breadcrumb_schema():
    return "http://schema.org/BreadcrumbList"


@register.inclusion_tag('breadcrumbs/breadcrumb_home.html')
def breadcrumb_home(url='/', title=''):
    return {
        'url': url,
        'title': title
    }


@register.inclusion_tag('breadcrumbs/breadcrumb_item.html')
def breadcrumb_item(url, title, position):
    return {
        'url': url,
        'title': title,
        'position': position
    }


@register.inclusion_tag('breadcrumbs/breadcrumb_active.html')
def breadcrumb_active(url, title, position):
    return {
        'url': url,
        'title': title,
        'position': position
    }