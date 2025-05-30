# reports/templatetags/report_extras.py
from django import template

register = template.Library()

@register.filter
def get_item(mapping, key):
    """
    Dict, defaultdict yoki istalgan mapping-dan elementni olish uchun:
        {{ my_dict|get_item:some_key }}
    Agar key topilmasa None qaytadi.
    """
    if mapping is None:
        return None
    return mapping.get(key)
