from django.urls import path

from . import views

urlpatterns = [
    path("mailme/", views.sendmail),
    path("preview/", views.preview),
    path("preview_iframe/", views.preview_iframe),
    path("", views.index),
]
