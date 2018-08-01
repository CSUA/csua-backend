from itertools import product
from django import forms
from django.contrib import admin

from .models import Event, Officer, Politburo, Sponsor

# Register your models here.
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass

class OfficerAdminForm(forms.ModelForm):
    blurb = forms.CharField(widget=forms.Textarea)
    office_hours = forms.CharField(
        widget=forms.Select(
            choices=[(choice, choice) for choice in
                [' '.join(oh) for oh in product(
                    [
                        "Mon",
                        "Tues",
                        "Wed",
                        "Thu",
                        "Fri",
                    ],
                    [
                        "10-11 AM",
                        "11-12 PM",
                        "12-1 PM",
                        "1-2 PM",
                        "2-3 PM",
                        "3-4 PM",
                        "4-5 PM",
                        "5-6 PM",
                        "6-7 PM",
                    ]
                )] + ["N/A"]
            ]))

@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'office_hours',
        'root_staff',
        'blurb',
        'enabled',
    )
    ordering = (
        '-enabled',
        'first_name',
        'last_name',
    )
    form = OfficerAdminForm

@admin.register(Politburo)
class PolituburoAdmin(admin.ModelAdmin):
    list_display = ('position', 'title', 'officer')
    ordering = ('position',)

@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    pass
