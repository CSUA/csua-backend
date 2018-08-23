import json
from urllib.request import urlopen
from urllib.parse import urlencode
import urllib.parse as urlparse

from django.utils.dateparse import parse_datetime
from django.http import HttpResponse

from apps.db_data.models import Event

GRAPH_URL = "https://graph.facebook.com/csua/events/"
GRAPH_TOKEN = "EAAGqPTSuTvcBAPoE7n6PGnN1rvZAzw2MYlFXRZCsKWZB7VrPZCAi8R7AmUjAKHDDmSlgMgx55sJnhRBMBrytQ1m6ehuup6K7CEZAgG9g9aoghmE1FbodYWVeZA9jZAUZAFfN9JBtZCZAGWjZAQ5XU9q2V03hy2HuZBrOrq3qMQf1Lo8XvkZCLbUI7ehjQ"
EVENT_URL = "https://www.facebook.com/events/{0}/"


def fetch_events(request):
    params = {"access_token": GRAPH_TOKEN}
    url_parts = list(urlparse.urlparse(GRAPH_URL))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    url = urlparse.urlunparse(url_parts)

    events_raw = urlopen(url).read()

    events = json.loads(events_raw)

    for event in events["data"]:
        try:
            event_obj = Event.objects.get(link=EVENT_URL.format(event["id"]))
        except Event.DoesNotExist:
            event_obj = Event(link=EVENT_URL.format(event["id"]))

        event_obj.name = event["name"]
        event_obj.location = event["place"]["name"]
        event_obj.description = event["description"]

        # Date looks like 2018-08-22T19:00:00-0700
        event_start_datetime = parse_datetime(event["start_time"])
        event_end_datetime = parse_datetime(event["end_time"])
        event_obj.date = event_start_datetime.date()
        event_obj.time = (
            event_start_datetime.time().strftime("%I:%M %p")
            + " - "
            + event_end_datetime.time().strftime("%I:%M %p")
        )

        event_obj.save()

    return HttpResponse(events_raw)
