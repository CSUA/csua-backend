from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin

from . import views

urlpatterns = [path("", views.index)]
