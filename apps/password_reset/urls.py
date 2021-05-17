from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import path

from . import views

app_name = "password_reset"

urlpatterns = [
    path("", views.RequestPasswordResetView, name="request-reset-password"),
    path("token/", views.RequestPasswordResetView, name="reset-password-token"),
    path(
        "reset-password-confirm/<uid>/<token>",
        views.PasswordResetView.as_view(),
        name="reset-password-confirm",
    ),
]
