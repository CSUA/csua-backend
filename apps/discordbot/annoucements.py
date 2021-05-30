import datetime

from django.utils import timezone

from apps.db_data.models import Event


def get_events_in_time_delta(requested_tdelta):
    """
    Retrieves a list of Event objects within the requested
    time delta.

    Handles the following requested_tdelta:
     - "week" (next week)
     - "tomorrow"
     - "today"
     - "hour" (in one hour)
     - "now" (in 10 minutes)
    """
    now = timezone.now().astimezone(timezone.get_current_timezone())
    events = get_events_in_time_range(*timeify(requested_tdelta))
    return events


def get_events_in_time_range(start_time, end_time):
    """
    Takes in a two datetime objects, start_time and end_time
    Returns events within the datetime range
    """
    events = Event.objects.filter(start_time__gte=start_time).filter(
        start_time__lte=end_time
    )
    return events


def timeify(requested_tdelta):
    """
    Converts requested_tdelta string into a corresponding datetime object
    """
    now = timezone.now()
    end_times = {
        "week": now + datetime.timedelta(weeks=1),
        "tomorrow": now + datetime.timedelta(days=1, hours=23, minutes=59, seconds=59),
        "today": now.replace(hour=23, minute=59, second=59),
        "hour": now + datetime.timedelta(hours=1, minutes=59, seconds=59),
        "now": now + datetime.timedelta(minutes=10),
    }
    start_times = {
        "week": now,
        "tomorrow": now + datetime.timedelta(days=1),
        "today": now,
        "hour": now + datetime.timedelta(hours=1),
        "now": now,
    }
    return start_times[requested_tdelta], end_times[requested_tdelta]
