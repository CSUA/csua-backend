from django.urls import path
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    path("politburo/", views.politburo),
    path("officers/", views.officers),
    path("sponsors/", views.sponsors),
    path("events/", views.EventsView.as_view()),
    path("events/workshops/", TemplateView.as_view(template_name="workshops.html")),
    path("api/db.json/", views.json),
]
