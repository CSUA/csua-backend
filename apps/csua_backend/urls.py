from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    path("", include("apps.main_page.urls")),
    path("", include("apps.db_data.urls")),
    path("outreach/", include("apps.outreach.urls")),
    path("admin/", admin.site.urls),
    path("newuser/", include("apps.newuser.urls")),
    path("computers/", include("apps.tracker.urls")),
    path("slack/", include("apps.philbot.urls")),
]
