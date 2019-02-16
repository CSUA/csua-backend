from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist

from .models import Item


def index(request):
    items = Item.objects.all()
    return render(request, "fridge/index.html", {"items": items})
