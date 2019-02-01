from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

import apps.fb_events.views
import apps.tracker.views

urlpatterns = [
    url(r"^admin/", admin.site.urls),
    url(r"^newuser/", include("apps.newuser.urls")),
    url(r"^computers/", include("apps.tracker.urls")),
]
