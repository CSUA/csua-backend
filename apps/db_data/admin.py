from django import forms
from django.contrib import admin

from .models import (
    Event,
    EventCategory,
    Notice,
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

admin.site.site_header = "CSUA Django Administration"
admin.site.site_title = "CSUA Administration"
admin.site.index_title = "Home"
admin.site.index_header = "Home"


class OfficershipAdminForm(forms.ModelForm):
    office_hours = forms.CharField(widget=forms.Select(choices=OH_CHOICES))
    tutor_subjects = forms.ModelMultipleChoiceField(
        required=False, queryset=UcbClass.objects, widget=forms.CheckboxSelectMultiple
    )


class SponsorshipInline(admin.TabularInline):
    model = Sponsorship
    ordering = ("sponsor__name",)
    autocomplete_fields = ("sponsor",)
    extra = 0


class OfficershipInline(admin.TabularInline):
    form = OfficershipAdminForm
    model = Officership
    autocomplete_fields = ("officer",)
    extra = 0


class PolitburoMembershipInline(admin.TabularInline):
    model = PolitburoMembership
    autocomplete_fields = ("person",)
    extra = 0


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    inlines = [OfficershipInline, PolitburoMembershipInline, SponsorshipInline]
    autocomplete_fields = ("events",)


@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    inlines = [OfficershipInline]
    list_display = ("person", "officer_since")
    ordering = ("person",)
    search_fields = (
        "person__user__first_name",
        "person__user__last_name",
        "person__user__username",
    )


@admin.register(Officership)
class OfficershipAdmin(admin.ModelAdmin):
    list_display = ("semester", "officer", "office_hours", "blurb")
    list_filter = ("semester", "officer")
    autocomplete_fields = ("tutor_subjects",)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    ordering = ("user",)
    list_display = ("user",)
    search_fields = ("user__first_name", "user__last_name", "user__username")


@admin.register(UcbClass)
class UcbClassAdmin(admin.ModelAdmin):
    search_fields = ("id",)


# Register your models here.
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    actions = ["duplicate_events", "enable_events", "disable_events"]
    search_fields = ("name", "date")

    def disable_events(modeladmin, request, queryset):
        queryset.update(enabled=False)

    def enable_events(modeladmin, request, queryset):
        queryset.update(enabled=True)

    def duplicate_events(modeladmin, request, queryset):
        for event in queryset:
            event.pk = None
            event.save()


@admin.register(Politburo)
class PolituburoAdmin(admin.ModelAdmin):
    inlines = [PolitburoMembershipInline]


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    inlines = [SponsorshipInline]
    search_fields = ("name",)


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ("expires", "text")
