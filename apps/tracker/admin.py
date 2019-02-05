from django.contrib import admin

from .models import User, Computer


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    readonly_fields = ["username", "last_ping"]
    list_display = ["username", "time_spent", "last_ping"]


@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    readonly_fields = ["local_timestamp"]
    list_display = ["hostname", "user"]
