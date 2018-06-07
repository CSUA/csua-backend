from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

admin.autodiscover()

urlpatterns = [
  url(r'^', include('main_page.urls')),
  url(r'^newuser/', include('newuser.urls')),
  url(r'^', include('db_data.urls')),
  url(r'^computers/', include('tracker.urls')),
  url(r'^~', include('homedirs.urls')),
  url(r'^admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
