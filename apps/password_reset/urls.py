from django.urls import path
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from . import views

urlpatterns = [
        path("", views.PasswordResetView, name="reset-password"),
        path("token/", views.PasswordResetView, name="reset-password-token"),
        path(r'^activate_account/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                views.ActivateAccountView.as_view(), name='activate_account'),
        ]
