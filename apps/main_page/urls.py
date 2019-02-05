from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

from . import views


urlpatterns = [
    url(r"^$", views.index),
    url(r"^hackathon13/$", views.hackathon13),
    url(r"^hackathon14/$", views.hackathon14),
    url(r"^hackathonsp15/$", views.hackathonsp15),
    url(r"^hackathonfa15/$", views.hackathonfa15),
    url(r"^hackathonsp16/$", views.hackathonsp16),
    url(r"^hackathonfa16/$", views.hackathonfa16),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
