from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  url(r'', include('main_page.urls')),
  url(r'newuser/', include('newuser.urls')),
  url(r'computers/', include('tracker.urls')),
  url(r'^admin/', include(admin.site.urls)),
)
