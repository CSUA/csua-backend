from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="discord_register"),
    path(
        "register-confirm/<email>/<discord_tag>/<token>/",
        views.register_confirm,
        name="discord_register_confirm",
    ),
]
