from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin

from . import views
from .admin_views import admin, admin_group, admin_user

urlpatterns = [
    path("", views.index),
    path("user/<username>/", views.user),
    path("user/<username>/groups/", views.user_groups),
    path("admin/", admin, name="ldap_admin"),
    path("admin/group/<groupname>/", admin_group, name="ldap_admin_group"),
    path("admin/user/<username>/", admin_user, name="ldap_admin_user"),
]
