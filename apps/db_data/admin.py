from django import forms
from django.contrib import admin

from .models import (
    Event,
    Officer,
    Officership,
    Person,
    Politburo,
    PolitburoMembership,
    Sponsor,
    Sponsorship,
    Semester,
    UcbClass,
)
from .constants import DAYS_OF_WEEK, OH_TIMES, OH_CHOICES


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    pass


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    pass


class OfficershipAdminForm(forms.ModelForm):
    office_hours = forms.CharField(widget=forms.Select(choices=OH_CHOICES))


@admin.register(Officership)
class OfficershipAdmin(admin.ModelAdmin):
    form = OfficershipAdminForm


@admin.register(UcbClass)
class UcbClassAdmin(admin.ModelAdmin):
    pass


# Register your models here.
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    actions = ["duplicate_events", "enable_events", "disable_events"]

    def disable_events(modeladmin, request, queryset):
        queryset.update(enabled=False)

    def enable_events(modeladmin, request, queryset):
        queryset.update(enabled=True)

    def duplicate_events(modeladmin, request, queryset):
        for event in queryset:
            event.pk = None
            event.save()


@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    pass


@admin.register(PolitburoMembership)
class PolituburoMembershipAdmin(admin.ModelAdmin):
    pass


@admin.register(Politburo)
class PolituburoAdmin(admin.ModelAdmin):
    pass

@admin.register(Sponsorship)
class SponsorshipAdmin(admin.ModelAdmin):
    pass

@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    pass
