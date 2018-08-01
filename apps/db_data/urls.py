from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^officers/$', views.officers),
    url(r'^politburo/$', views.politburo),
    url(r'^sponsors/$', views.sponsors),
    url(r'^api/db.json$', views.json),
]
