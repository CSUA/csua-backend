from django.urls import path
from . import views

urlpatterns = [
    path("event/", views.SlackEventAPI.as_view()),
    path("command/", views.SlackCommandAPI.as_view()),
]
