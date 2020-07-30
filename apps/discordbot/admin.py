from django.contrib import admin
from .models import DiscordRegisteredUser

# Register your models here.
@admin.register(DiscordRegisteredUser)
class DiscordRegisteredUserAdmin(admin.ModelAdmin):
    list_display = ("email", "discord_tag", "timestamp")
