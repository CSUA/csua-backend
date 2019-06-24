import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView
from django.views.decorators.cache import cache_page

from .models import (
    Event,
    Officer,
    Politburo,
    Sponsor,
    Sponsorship,
    Semester,
    Officership,
    PolitburoMembership,
)
from .constants import DAYS_OF_WEEK, OH_TIMES


class EventsView(TemplateView):
    template_name = "events.html"

    def get_context_data(request):
        context = {}
        semester = Semester.objects.filter(current=True).get()
        context["events"] = semester.events.all()
        return context


# @cache_page(3 * 60)
def officers(request, semester_id=None):
    if semester_id is None:
        semester = Semester.objects.filter(current=True).get()
    else:
        semester = get_object_or_404(Semester, id=semester_id)
    officerships = (
        Officership.objects.filter(semester=semester)
        .select_related("officer__person__user")
        .order_by("officer__person__user__first_name")
    )
    print(officerships.all())

    for officership in officerships:
        print(officership)

    office_hours_calendar = [
        [hour]
        + [officerships.filter(office_hours=day + " " + hour) for day in DAYS_OF_WEEK]
        for hour in OH_TIMES
    ]

    calendar = {
        "days": DAYS_OF_WEEK,
        "hours": OH_TIMES,
        "contents": office_hours_calendar,
    }
    return render(
        request,
        "officers.html",
        {"officer_list": officerships, "calendar": calendar, "semester": semester},
    )


def politburo(request, semester_id=None):
    if semester_id is None:
        semester = Semester.objects.filter(current=True).get()
    else:
        semester = get_object_or_404(Semester, id=semester_id)

    pb = (
        PolitburoMembership.objects.filter(semester=semester)
        .select_related("person__user")
        .order_by("id")
    )

    return render(request, "politburo.html", {"pb": pb})


def sponsors(request, semester_id=None):
    if semester_id is None:
        semester = Semester.objects.filter(current=True).get()
    else:
        semester = get_object_or_404(Semester, id=semester_id)
    sponsorships = (
        Sponsorship.objects.select_related("sponsor")
        .filter(semester=semester)
        .order_by("sponsor__name")
    )
    return render(
        request,
        "sponsors.html",
        {"sponsorships": sponsorships},
    )
