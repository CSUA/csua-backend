from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist


def index(request):
    return render(request, "index.html")


def workshops(request):
    return render(request, "workshops.html")


def hackathon13(request):
    return render(request, "hackathonfa13.html")


def hackathon14(request):
    return render(request, "hackathonfa14.html")


def hackathonsp15(request):
    return render(request, "hackathonsp15.html")


def hackathonfa15(request):
    return render(request, "index.html")


def hackathonsp16(request):
    return render(request, "hackathonsp16.html")


def hackathonfa16(request):
    return render(request, "hackathonfa16.html")
