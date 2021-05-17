from django.urls import path
from django.views.generic.base import TemplateView

from . import staff_views, views

urlpatterns = [
    path("politburo/", views.politburo, name="politburo"),
    path("politburo/<semester_id>", views.politburo, name="politburo_semester"),
    path("officers/", views.officers, name="officers"),
    path("add-officer/", staff_views.update_or_create_officer, name="add-officer"),
    path("time-machine/", staff_views.update_semester, name="update_semester"),
    path("officers/<semester_id>/", views.officers, name="officers_semester"),
    path("sponsors/", views.sponsors, name="sponsors"),
    path("events/", TemplateView.as_view(template_name="events.html"), name="events"),
    path(
        "events/workshops/",
        TemplateView.as_view(template_name="workshops.html"),
        name="workshops",
    ),
    path("tutoring/", views.tutoring, name="tutoring"),
]
