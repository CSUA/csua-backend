from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.autodiscover()

urlpatterns = [
    path("", include("apps.main_page.urls")),
    path("", include("apps.db_data.urls")),
    path("ldap/", include("apps.ldap.urls")),
    path("outreach/", include("apps.outreach.urls")),
    path("admin/", admin.site.urls),
    path("newuser/", include("apps.newuser.urls")),
    path("computers/", include("apps.tracker.urls")),
    path("slack/", include("apps.slackbot.urls")),
    path("discord/", include("apps.discordbot.urls")),
    path(
        "reset-password/",
        include("apps.password_reset.urls", namespace="password_reset"),
    ),
]
