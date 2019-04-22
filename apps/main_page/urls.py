from django.conf import settings
from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from django.contrib.auth.views import LoginView, LogoutView

from . import views
from apps.db_data.views import EventsView

urlpatterns = [
    re_path(r"^$", EventsView.as_view(template_name="index.html")),
    path("constitution/", TemplateView.as_view(template_name="constitution.html")),
    path("join/", TemplateView.as_view(template_name="join.html")),
    path("tutoring/", TemplateView.as_view(template_name="tutoring.html")),
    path("alumni/", TemplateView.as_view(template_name="alumni.html")),
    path("login/", LoginView.as_view(template_name="registration/login.html")),
    path("logout/", LogoutView.as_view()),
    path("hackathon14/", views.hackathon14),
    path("hackathonsp15/", views.hackathonsp15),
    path("hackathonfa15/", views.hackathonfa15),
    path("hackathonsp16/", views.hackathonsp16),
    path("hackathonfa16/", views.hackathonfa16),
    path("404/", TemplateView.as_view(template_name="404.html")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
