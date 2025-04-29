from django import template
from django.core.cache import cache

register = template.Library()


@register.inclusion_tag("calendar.html")
def calendar():
    events = cache.get("calendar_events", [])
    return {"events": events}
