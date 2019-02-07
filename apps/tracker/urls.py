from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("ping/<code_text>/<signature>/", views.ping),
    path("json/", views.json),
]
