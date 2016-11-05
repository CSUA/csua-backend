from django.conf.urls import patterns, url
from db_data import views

urlpatterns = [
    url(r'^officers/$', views.officers),
    url(r'^politburo/$', views.politburo),
    url(r'^sponsors/$', views.sponsors),
    ]
