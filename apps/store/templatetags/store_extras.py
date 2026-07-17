from django import template
from django.utils.safestring import mark_safe
from collections import OrderedDict as SortedDict
import bleach
import os

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


@register.simple_tag
def responsive_img(image_field, alt='', css_class='', loading='lazy', sizes=None):
    """
    Render an <img> with srcset for responsive images.

    Usage:
        {% responsive_img product.image "Product title" css_class="image" loading="lazy" %}

    Generates srcset with _sm (400w), _md (800w), and full-size variants.
    Falls back to plain <img src> if field is empty.
    """
    if not image_field or not image_field.name:
        return ''

    url = image_field.url
    base, ext = os.path.splitext(url)

    # Build srcset: try _sm and _md variants, fall back to full
    srcset_parts = []
    for suffix, width in [('sm', 400), ('md', 800)]:
        variant_url = f'{base}_{suffix}{ext}'
        srcset_parts.append(f'{variant_url} {width}w')
    srcset_parts.append(f'{url} 1200w')

    srcset = ', '.join(srcset_parts)

    if sizes is None:
        sizes = '(max-width: 600px) 100vw, (max-width: 1024px) 50vw, 33vw'

    attrs = [
        f'src="{url}"',
        f'srcset="{srcset}"',
        f'sizes="{sizes}"',
        f'alt="{alt}"',
    ]
    if css_class:
        attrs.append(f'class="{css_class}"')
    if loading:
        attrs.append(f'loading="{loading}"')

    return mark_safe(f'<img {" ".join(attrs)}>')
