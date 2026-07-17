from django import template
from collections import OrderedDict as SortedDict
import bleach

register = template.Library()

ALLOWED_TAGS = list(bleach.ALLOWED_TAGS) + ['p', 'br', 'h1', 'h2', 'h3', 'h4', 'ul', 'ol', 'li', 'span', 'div', 'table', 'thead', 'tbody', 'tr', 'th', 'td']
ALLOWED_ATTRIBUTES = dict(bleach.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRIBUTES['a'] = ['href', 'title', 'target']
ALLOWED_ATTRIBUTES['img'] = ['src', 'alt', 'width', 'height']
ALLOWED_ATTRIBUTES['td'] = ['colspan', 'rowspan']
ALLOWED_ATTRIBUTES['th'] = ['colspan', 'rowspan']

@register.filter
def sanitize_html(value):
    """Sanitize HTML to prevent XSS while keeping safe formatting tags."""
    if not value:
        return value
    return bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)

@register.filter
def variable_by_var(variables, var):
    filtered_var = variables.filter(varitem = var).first()
    return filtered_var

# @register.filter
# def listsort(value):
#     if isinstance(value, dict):
#         new_dict = SortedDict()
#         key_list = sorted(value.keys())
#         for key in key_list:
#             new_dict[key] = value[key]
#         return new_dict
#     elif isinstance(value, list):
#         return sorted(value)
#     else:
#         return value
#     listsort.is_safe = True

@register.filter
def category_sort(categories, order):
    filtered_cat = categories.order_by(order)
    return filtered_cat


@register.filter
def dict_get(d, key):
    return d.get(key, [])


@register.filter
def is_visible(products):
	is_visible__products = products.filter(is_visible = True)
	return is_visible__products

@register.inclusion_tag('product_card.html')
def product_card(product):
    return {
        'p': product,
    }
