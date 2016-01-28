from django.conf.urls import patterns, url
from newuser import views

urlpatterns = [
    url(r'^$',views.index),
    url(r'^auth/$', views.auth),
    url(r'^verify/$', views.verify),
    ]
