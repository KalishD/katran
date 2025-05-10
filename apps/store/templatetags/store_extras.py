from django import template
from collections import OrderedDict as SortedDict
register = template.Library()

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
