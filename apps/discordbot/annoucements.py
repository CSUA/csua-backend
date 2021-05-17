import datetime

import pytz
from django.utils import timezone

from apps.db_data.models import Event


def get_events_in_date_or_time_delta(requested_tdelta):
    """
    Checks events in db to see if any match the day
    """
    now = timezone.now().astimezone(pytz.timezone("US/Pacific"))
    events = get_events_in_time_range(timeify(requested_tdelta))
    return events


def get_events_in_time_range(range):
    """
    Takes in a tuple from timeify
    Returns events in the datetime range
    """
    events = Event.objects.filter(date_time__gte=range[0]).filter(
        date_time__lte=range[1]
    )
    return events


def timeify(requested_tdelta):
    """
    Converts requested_tdelta string into a corresponding datetime object
    """
    now = timezone.now()
    end_times = {
        "week": now + datetime.timedelta(weeks=1),
        "tomorrow": (now + datetime.timedelta(days=1)).replace(
            hour=23, minute=59, second=59
        ),
        "today": now.replace(hour=23, minute=59, second=59),
        "hour": (now + datetime.timedelta(hours=1)).replace(minute=59, second=59),
        "now": now + datetime.timedelta(minutes=10),
    }
    start_times = {
        "week": now,
        "tomorrow": (now + datetime.timedelta(days=1)).replace(
            hour=0, minute=0, second=0
        ),
        "today": now,
        "hour": (now + datetime.timedelta(hours=1)).replace(minute=0, second=0),
        "now": now,
    }
    return start_times[requested_tdelta], end_times[requested_tdelta]
