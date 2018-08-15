from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.index),
    url(r"^ping/(?P<code_text>.+)/(?P<signature>.+)$", views.ping),
]
