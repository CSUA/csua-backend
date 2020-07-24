from django.urls import path
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from . import views

urlpatterns = [
    path("token/", views.RequestPasswordResetView, name="reset-password-token"),
    path(
        "reset-password-confirm/<uid>/<token>",
        views.PasswordResetView.as_view(),
        name="reset-password-confirm",
    ),
    path("", views.RequestPasswordResetView, name="request-reset-password"),
]
