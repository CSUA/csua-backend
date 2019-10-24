from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin

from . import views

urlpatterns = [
    path("", views.index),
    path("group/<groupname>/", views.group),
    path("user/<username>/", views.user),
    path("user/<username>/groups/", views.user_groups),
]
