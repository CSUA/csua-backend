from django import template
from django.utils import timezone

from apps.db_data.models import Event, Notice

register = template.Library()


@register.simple_tag
def get_upcoming_events():
    return Event.objects.filter(start_time__gte=timezone.now())


@register.simple_tag
def get_current_notices():
    return Notice.objects.filter(expires__gte=timezone.now().date())
