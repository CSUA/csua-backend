from django.urls import path
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from . import views

urlpatterns = [
    path("", views.RequestPasswordResetView, name="request-reset-password"),
    path("token/", views.RequestPasswordResetView, name="reset-password-token"),
    path(
        "activate_account/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        views.PasswordResetView.as_view(),
        name="reset-password",
    ),
]
