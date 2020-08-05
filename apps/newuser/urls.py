from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="newuser"),
    path("remote/", views.request_remote_newuser, name="newuser-remote-request"),
    path("remote/<email>/<token>/", views.remote_newuser, name="newuser-remote"),
]
