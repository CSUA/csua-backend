from django.conf.urls import url
from django.contrib import admin
from .views import SlackAPI

urlpatterns = [
    url(r'^$', SlackAPI.as_view())
]
