from django.conf.urls import patterns, url
from db_data import views

urlpatterns = [
    url(r'^$',views.index),
    ]
