# inventory/templatetags/inventory_extras.py
from django import template

register = template.Library()

@register.filter
def intgte(value, arg=0):
    """
    True qaytaradi, agar value >= arg bo‘lsa.
    {{ some_number|intgte:0 }}
    """
    try:
        return int(value) >= int(arg)
    except (TypeError, ValueError):
        return False
