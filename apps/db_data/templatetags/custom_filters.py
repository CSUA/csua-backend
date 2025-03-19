from django import template

register = template.Library()


@register.filter
def index(list, i):
    return list[i] if i < len(list) else None
