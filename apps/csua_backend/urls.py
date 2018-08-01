from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    url(r'^', include("apps.main_page.urls")),
    url(r'^newuser/', include('apps.newuser.urls')),
    url(r'^', include('apps.db_data.urls')),
    url(r'^computers/', include('apps.tracker.urls')),
    url(r'^~', include('apps.homedirs.urls')),
    url(r'^admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
