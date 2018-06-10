from django.contrib import admin

from .models import Event, Officer, Politburo, Sponsor

# Register your models here.
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass

@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'office_hours', 'root_staff', 'blurb')
    ordering = ('first_name', 'last_name')

@admin.register(Politburo)
class PolituburoAdmin(admin.ModelAdmin):
    list_display = ('position', 'title', 'officer')
    ordering = ('position',)

@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    pass
