import datetime
from enum import Enum

from django.utils import timezone

from apps.db_data.models import Event


class AnnouncementType(Enum):
    WEEK = "week"
    TOMORROW = "tomorrow"
    TODAY = "today"
    HOUR = "hour"
    B_TIME = "now"  # Berkeley Time


def get_events_in_time_delta(requested_atype: AnnouncementType):
    """
    Retrieves a list of Event objects within the requested
    time delta.

    requested_atype will take in enum constants in
    AnnouncementType
    """
    now = timezone.now().astimezone(timezone.get_current_timezone())
    events = get_events_in_time_range(*timeify(requested_atype))
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


def timeify(requested_atype: AnnouncementType):
    """
    Converts requested_tdelta string into a corresponding datetime object
    """
    now = timezone.now()
    time_ranges = {
        AnnouncementType.WEEK: (now, now + datetime.timedelta(weeks=1)),
        AnnouncementType.TOMORROW: (
            now + datetime.timedelta(days=1),
            now + datetime.timedelta(days=1, hours=23, minutes=59, seconds=59),
        ),
        AnnouncementType.TODAY: (
            now,
            now + datetime.timedelta(hours=23, minutes=59, seconds=59),
        ),
        AnnouncementType.HOUR: (
            now + datetime.timedelta(hours=1),
            now + datetime.timedelta(hours=1, minutes=59, seconds=59),
        ),
        AnnouncementType.B_TIME: (now, now + datetime.timedelta(minutes=10)),
    }
    return time_ranges[requested_atype]
