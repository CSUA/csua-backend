from datetime import datetime

from django import template

register = template.Library()


@register.filter
def index(list, i):
    return list[i] if i < len(list) else None


@register.filter
def parse_iso(value):
    """
    Convert an ISO formatted date/time string to a datetime object.
    Returns None if conversion fails.
    """
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


@register.filter(is_safe=True)
def label_with_classes(value, arg):
    return value.label_tag(attrs={"class": arg})
