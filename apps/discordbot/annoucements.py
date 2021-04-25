import datetime
from apps.db_data.models import Event

def event_checker(requested_tdelta):
    """
    Checks events in db to see if any match the day
    """
    today = datetime.date.today()
    now = datetime.datetime.now()
    upcoming_events = Event.objects.filter(date__gte=today).filter(time__gte=now)
    days = {
            "week": today + datetime.timedelta(weeks=1),
            "tomorrow": today + datetime.timedelta(days=1),
            "today": today,
        }
    times = {
            "hour": now + datetime.timedelta(hours=1),
            "now": now + datetime.timedelta(minutes=1)
        }
    if requested_tdelta in times:
        events = Event.objects \
                    .filter(date=today, time__lte=times[requested_tdelta]) \
                    .filter(time__gte=now) \
                    .order_by("time")
    else:
        events = Event.objects.filter(date=days[requested_tdelta]).order_by("time")
    return events
