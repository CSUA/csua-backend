from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="newuser"),
    path("remote/", views.remote_newuser, name="remote"),
    path(
        "remote/<token>", views.RemoteCreateNewUserView.as_view(), name="remote-create"
    ),
]
