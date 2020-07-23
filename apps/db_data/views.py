import datetime
import codecs
from collections import defaultdict

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_safe
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required

from .models import (
    Notice,
    Event,
    Officer,
    Politburo,
    Person,
    Sponsor,
    Sponsorship,
    Semester,
    Officership,
    PolitburoMembership,
    UcbClass,
)
from .constants import DAYS_OF_WEEK, OH_TIMES
from .forms import OfficerCreationForm
from apps.ldap.utils import user_exists, is_root, add_officer, is_officer

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
    }
    print(officerships)
    return render(
        request,
        "officers.html",
        {
            "officer_list": officerships,
            "calendar": calendar,
            "semester": semester,
            "semesters": semesters,
        },
    )


@staff_member_required
def update_or_create_officer(request):
    semester = Semester.objects.filter(current=True).get()
    if request.method == "POST":
        form = OfficerCreationForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            if user_exists(username):

                user, created = User.objects.get_or_create(username=username)
                if created:
                    messages.info(request, "User {username} created")

                defaults = {}
                photo = form.cleaned_data.get("photo")
                if photo:
                    messages.info(request, "Updated photo")
                    defaults.update(photo1=photo)
                else:
                    photo_url = form.cleaned_data.get("photo_url")
                    # TODO: download photo
                photo2 = form.cleaned_data.get("photo2")
                if photo2:
                    messages.info(request, "Updated photo2")
                    defaults.update(photo2=photo)
                else:
                    photo2_url = form.cleaned_data.get("photo2_url")
                    # TODO: download photo
                person, created = Person.objects.update_or_create(
                    user=user, defaults=defaults
                )
                person.save()
                if created:
                    messages.info(request, f"Person {username} created")

                root_staff = is_root(username)
                defaults = {"root_staff": root_staff}
                officer_since = form.cleaned_data.get("officer_since")
                if officer_since:
                    defaults.update(officer_since=officer_since)
                    messages.info(request, f"Officer since updated to {officer_since}")
                officer, created = Officer.objects.update_or_create(
                    person=person, defaults=defaults
                )
                if created:
                    messages.info(request, f"Officer {username} created")

                blurb = form.cleaned_data.get("blurb")
                office_hours = form.cleaned_data.get("office_hours")
                defaults = {}
                if blurb:
                    defaults.update(blurb=blurb)
                    messages.info(request, "Blurb updated")
                if office_hours:
                    defaults.update(office_hours=office_hours)
                    messages.info(request, f"Office hour updated to {office_hours}")
                officership = Officership.objects.update_or_create(
                    officer=officer, semester=semester, defaults=defaults
                )

                if not is_officer(username):
                    success, msg = add_officer(username)
                    if success:
                        messages.info(
                            request, f"Added {username} to officers LDAP group"
                        )
                    else:
                        messages.error(
                            request,
                            f"Failed to add {username} to officers LDAP group: {msg}",
                        )
                messages.info(request, f"{username} updated")
                return HttpResponseRedirect(reverse("add-officer"))
            else:
                messages.error(request, f"User {username} does not exist in LDAP")
    else:
        form = OfficerCreationForm()

    return render(request, "add_officer.html", {"form": form, "semester": semester})


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
