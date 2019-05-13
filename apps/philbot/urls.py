from django.conf.urls import url
from django.contrib import admin
from .views import SlackEventAPI, SlackCommandAPI
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    url(r"^event/$", SlackEventAPI.as_view()),
    url(r"^command/$", SlackCommandAPI.as_view()),
]
