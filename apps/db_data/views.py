import codecs
from collections import defaultdict
from datetime import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_safe
from django.views.generic.base import TemplateView

from apps.ldap.utils import add_officer, is_officer, is_root, user_exists

from .constants import DAYS_OF_WEEK, OH_TIME_MAP, OH_TIMES
from .forms import OfficerCreationForm
from .models import (
    Event,
    Notice,
    Officer,
    Officership,
    Person,
    Politburo,
    PolitburoMembership,
    Semester,
    Sponsor,
    Sponsorship,
    UcbClass,
)


# @cache_page(3 * 60)
def officers(request, semester_id=None):
    if semester_id is None:
        semester = Semester.objects.filter(current=True).get()
    else:
        semester = get_object_or_404(Semester, id=semester_id)
    semesters = Semester.objects.exclude(id=semester.id)
    officerships = (
        Officership.objects.filter(semester=semester)
        .select_related("officer__person__user")
        .order_by("officer__person__user__first_name")
    )

    office_hours_calendar = [
        [hour]
        + [officerships.filter(office_hours=day + " " + hour) for day in DAYS_OF_WEEK]
        for hour in OH_TIMES
    ]

    calendar = {
        "days": DAYS_OF_WEEK,
        "hours": OH_TIMES,
        "contents": office_hours_calendar,
        "ohTimeMap": OH_TIME_MAP,
    }

    current_hour = datetime.now().strftime("%H")
    current_timeslot = OH_TIME_MAP.get(int(current_hour))

    current_minute = datetime.now().minute
    current_hour_pct = (current_minute / 60) * 100

    return render(
        request,
        "officers.html",
        {
            "officer_list": officerships,
            "calendar": calendar,
            "semester": semester,
            "semesters": semesters,
            "current_timeslot": current_timeslot,
            "current_hour_pct": current_hour_pct,
        },
    )


def politburo(request, semester_id=None):
    if semester_id is None:
        semester = Semester.objects.filter(current=True).get()
    else:
        semester = get_object_or_404(Semester, id=semester_id)
    semesters = Semester.objects.exclude(id=semester.id)

    pb = (
        PolitburoMembership.objects.filter(semester=semester)
        .select_related("person__user")
        .order_by("id")
    )

    return render(request, "politburo.html", {"pb": pb, "semesters": semesters})


def semester_ordering_key(semester):
    return (semester.id[2:] + codecs.encode(semester.id[:2], "rot13"),)


def sponsors(request):
    semesters = Semester.objects.all()
    sponsorships = Sponsorship.objects.all()
    sponsorships_by_semester = defaultdict(list)
    for sponsorship in sponsorships:
        sponsorships_by_semester[sponsorship.semester].append(sponsorship)
    sponsorships_by_semester = sorted(
        sponsorships_by_semester.items(),
        key=lambda pair: semester_ordering_key(pair[0]),
        reverse=True,
    )
    for semester, sponsorships in sponsorships_by_semester:
        sponsorships.sort(key=lambda sponsorship: sponsorship.sponsor.name)

    return render(
        request, "sponsors.html", {"sponsorships_by_semester": sponsorships_by_semester}
    )


def tutoring(request, semester_id=None):
    if semester_id is None:
        semester = Semester.objects.filter(current=True).get()
    else:
        semester = get_object_or_404(Semester, id=semester_id)
    officerships = Officership.objects.select_related("officer").filter(
        semester=semester
    )
    all_tutoring_subjects = UcbClass.objects.all()
    tutors_by_subject = {}
    for subject in all_tutoring_subjects:
        tutors_by_subject[str(subject)] = [
            officership.officer
            for officership in officerships
            if subject in officership.tutor_subjects.all()
        ]
    return render(request, "tutoring.html", {"tutors_by_subject": tutors_by_subject})


# acts as a sort key for semesters(terms) so they're in the correct chronological order (sp21 < fa22)
# term follows pattern <semester><year>, e.g. sp21, fa22
def term_sort_key(term):
    term_id = term.id
    semester = term_id[:2]
    year = int(term_id[2:])

    semester_order = 0 if semester == "sp" else 1

    return year, semester_order


def archives(request):
    semesters = Semester.objects.all()
    sorted_semesters = sorted(semesters, key=term_sort_key, reverse=True)

    return render(
        request,
        "archives.html",
        context={
            "sorted_semesters": sorted_semesters,
        },
    )
