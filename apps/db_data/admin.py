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

# Register your models here.
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    ordering = ["enabled", "date"]
    list_display = ["name", "date", "time", "link", "enabled"]
    actions = ["duplicate_events", "enable_events", "disable_events"]

    def disable_events(modeladmin, request, queryset):
        queryset.update(enabled=False)

    def enable_events(modeladmin, request, queryset):
        queryset.update(enabled=True)

    def duplicate_events(modeladmin, request, queryset):
        for event in queryset:
            event.pk = None
            event.save()


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
