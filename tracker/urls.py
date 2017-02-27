from django.conf.urls import patterns, url
from tracker import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^ping/(?P<codeText>.+)/(?P<signature>.+)$', views.ping),
    ]
