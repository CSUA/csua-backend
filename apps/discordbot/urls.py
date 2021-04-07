from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="discord_register"),
    path(
        "register-sent/<emailb64>/",
        views.email_sent,
        name="discord_register_email_sent",
    ),
    path(
        "register-confirm/<emailb64>/<discord_tagb64>/<token>/",
        views.register_confirm,
        name="discord_register_confirm",
    ),
]
