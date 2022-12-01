from django import template
register = template.Library()

@register.filter
def variable_by_var(variables, var):
    filtered_var = variables.filter(varitem = var).first()
    return filtered_var