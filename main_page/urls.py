from django.conf.urls import patterns, url
from main_page import views

urlpatterns = [
    url(r'^$',views.index),
    url(r'^about/$', views.about),
    url(r'^constitution/$', views.constitution),
    url(r'^donate/$', views.donate),
    url(r'^events/$', views.events),
    url(r'^index/$', views.index),
    url(r'^industry/$', views.industry),
    url(r'^join/$', views.join),
    url(r'^officers/$', views.officers),
    url(r'^politburo/$', views.politburo),
    ]
