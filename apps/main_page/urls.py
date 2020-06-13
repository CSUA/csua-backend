from django.conf import settings
from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from django.contrib.auth.views import LoginView, LogoutView

from . import views

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path(
        "constitution/",
        TemplateView.as_view(template_name="constitution.html"),
        name="constitution",
    ),
    path(
        "resources/",
        TemplateView.as_view(template_name="computing_resources.html"),
        name="computing_resources",
    ),
    path("join/", TemplateView.as_view(template_name="join.html"), name="join"),
    path("alumni/", TemplateView.as_view(template_name="alumni.html"), name="alumni"),
    path(
        "login/",
        LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "contact/", TemplateView.as_view(template_name="contact.html"), name="contact"
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="my_profile"),
    path("profile/<username>/", views.profile, name="profile"),
    path("404/", TemplateView.as_view(template_name="404.html")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
