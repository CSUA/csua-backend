from django.contrib import admin
from .models import Officer, Politburo, Sponsor, Event

# Register your models here.
admin.site.register(Officer)
admin.site.register(Politburo)
admin.site.register(Sponsor)
admin.site.register(Event)
