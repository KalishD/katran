from django import template
register = template.Library()

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
    return "https://schema.org/BreadcrumbList"


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