import json
from urllib.request import urlopen
from urllib.parse import urlencode
import urllib.parse as urlparse

from django import forms
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.utils.dateparse import parse_datetime

from .models import Event, Officer, Politburo, Sponsor
from .constants import DAYS_OF_WEEK, OH_TIMES, OH_CHOICES

GRAPH_URL = "https://graph.facebook.com/csua/events/"
GRAPH_TOKEN = "EAAGqPTSuTvcBAPoE7n6PGnN1rvZAzw2MYlFXRZCsKWZB7VrPZCAi8R7AmUjAKHDDmSlgMgx55sJnhRBMBrytQ1m6ehuup6K7CEZAgG9g9aoghmE1FbodYWVeZA9jZAUZAFfN9JBtZCZAGWjZAQ5XU9q2V03hy2HuZBrOrq3qMQf1Lo8XvkZCLbUI7ehjQ"
EVENT_URL = "https://www.facebook.com/events/{0}/"

# Register your models here.
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    ordering = ["date"]
    list_display = ["name", "date", "time", "link"]

    def fetch_events(self, request):
        params = {"access_token": GRAPH_TOKEN}
        url_parts = list(urlparse.urlparse(GRAPH_URL))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urlencode(query)
        url = urlparse.urlunparse(url_parts)
        events_raw = urlopen(url).read().decode()
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

    change_list_template = "db_data/event_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path("fetch-events/", self.fetch_events)]
        return my_urls + urls


class OfficerAdminForm(forms.ModelForm):
    blurb = forms.CharField(widget=forms.Textarea)
    office_hours = forms.CharField(widget=forms.Select(choices=OH_CHOICES))


@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "office_hours",
        "root_staff",
        "blurb",
        "enabled",
    ]
    ordering = ["-enabled", "first_name", "last_name"]
    form = OfficerAdminForm

    actions = ["disable_officer", "enable_officer"]

    def disable_officer(modeladmin, request, queryset):
        queryset.update(enabled=False)

    def enable_officer(modeladmin, request, queryset):
        queryset.update(enabled=True)


@admin.register(Politburo)
class PolituburoAdmin(admin.ModelAdmin):
    list_display = ["position", "title", "officer"]
    ordering = ["position"]


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ["name", "url", "description", "current"]

    actions = ["disable_sponsor", "enable_sponsor"]

    def disable_sponsor(modeladmin, request, queryset):
        queryset.update(current=False)

    def enable_sponsor(modeladmin, request, queryset):
        queryset.update(current=True)
