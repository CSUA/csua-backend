from django.contrib import admin

from .models import AniShuffleGame, ConnectFourGame, DiscordRegisteredUser


# Register your models here.
@admin.register(DiscordRegisteredUser)
class DiscordRegisteredUserAdmin(admin.ModelAdmin):
    list_display = ("email", "discord_tag", "timestamp")


@admin.register(ConnectFourGame)
class ConnectFourGameAdmin(admin.ModelAdmin):
    pass


@admin.register(AniShuffleGame)
class AniShuffleGameAdmin(admin.ModelAdmin):
    pass
