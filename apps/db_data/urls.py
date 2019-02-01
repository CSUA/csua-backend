from django.conf.urls import url

from . import views

urlpatterns = [url(r"^api/db.json$", views.json)]
