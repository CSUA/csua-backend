from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

from fiber.views import page
import apps.fb_events.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^admin/fiber/', include('fiber.admin_urls')),
    url(r'^api/v2/', include('fiber.rest_api.urls')),
    url(r'^newuser/', include('apps.newuser.urls')),
    url(r'^computers/', include('apps.tracker.urls')),
    url(r'^api/events/', apps.fb_events.views.fetch_events),
    url(r'^~', include('apps.homedirs.urls')),
    url(r'', include('apps.db_data.urls')),
    url(r'^', include("apps.main_page.urls")),
    url(r'', page),
]
