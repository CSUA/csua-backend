import json
from urllib.request import urlopen
from urllib.parse import urlencode
import urllib.parse as urlparse

from django.http import HttpResponse

from apps.db_data.models import Event

GRAPH_URL = "https://graph.facebook.com/csua/events/"
GRAPH_TOKEN = "EAAGqPTSuTvcBAPoE7n6PGnN1rvZAzw2MYlFXRZCsKWZB7VrPZCAi8R7AmUjAKHDDmSlgMgx55sJnhRBMBrytQ1m6ehuup6K7CEZAgG9g9aoghmE1FbodYWVeZA9jZAUZAFfN9JBtZCZAGWjZAQ5XU9q2V03hy2HuZBrOrq3qMQf1Lo8XvkZCLbUI7ehjQ"


def fetch_events(request):
    params = {"access_token": GRAPH_TOKEN}
    url_parts = list(urlparse.urlparse(GRAPH_URL))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urlencode(query)
    url = urlparse.urlunparse(url_parts)

    events_raw = urlopen(url).read()

    events = json.loads(events_raw)
    return HttpResponse(events_raw)
