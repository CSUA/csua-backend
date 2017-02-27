from django.conf.urls import patterns, url
from newuser import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^create/$', views.create),
    ]
