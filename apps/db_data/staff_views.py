from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User

from .models import (
    Officer,
    Officership,
    Person,
    Semester,
    Politburo,
    PolitburoMembership,
)
from .forms import OfficerCreationForm
from apps.ldap.utils import is_root, is_officer, add_officer


@staff_member_required
def update_or_create_officer(request):
    semester = Semester.objects.filter(current=True).get()
    if request.method == "POST":
        form = OfficerCreationForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            blurb = form.cleaned_data.get("blurb")
            office_hours = form.cleaned_data.get("office_hours")
            photo = form.cleaned_data.get("photo")
            photo_url = form.cleaned_data.get("photo_url")
            photo2 = form.cleaned_data.get("photo2")
            photo2_url = form.cleaned_data.get("photo2_url")
            officer_since = form.cleaned_data.get("officer_since")
            _update_or_create_officer(
                request,
                username,
                photo,
                photo_url,
                photo2,
                photo2_url,
                officer_since,
                blurb,
                office_hours,
                semester,
            )
            return HttpResponseRedirect(reverse("add-officer"))
    else:
        form = OfficerCreationForm()

    return render(request, "add_officer.html", {"form": form, "semester": semester})


def _update_or_create_officer(
    request,
    username,
    photo,
    photo_url,
    photo2,
    photo2_url,
    officer_since,
    blurb,
    office_hours,
    semester,
):
    user, created = User.objects.get_or_create(username=username)
    if created:
        messages.info(request, f"User {username} created")

    defaults = {}
    if photo:
        messages.info(request, f"Updated photo1 for {username}")
        defaults.update(photo1=photo)
    elif photo_url:
        ...
        # TODO: download photo
        messages.warning(request, f"Using photo_url is not yet supported")
    if photo2:
        messages.info(request, f"Updated photo2 for {username}")
        defaults.update(photo2=photo)
    elif photo2_url:
        ...
        # TODO: download photo
        messages.warning(request, f"Using photo2_url is not yet supported")
    person, created = Person.objects.update_or_create(user=user, defaults=defaults)
    person.save()
    if created:
        messages.info(request, f"Person {username} created")

    root_staff = is_root(username)
    defaults = {"root_staff": root_staff}
    if officer_since:
        defaults.update(officer_since=officer_since)
        messages.info(
            request, f"Officer {username} start date updated to {officer_since}"
        )
    officer, created = Officer.objects.update_or_create(
        person=person, defaults=defaults
    )
    if created:
        messages.info(request, f"Officer {username} created")

    defaults = {}
    if blurb:
        defaults.update(blurb=blurb)
        messages.info(request, f"Updated blurb of {username}")
    if office_hours:
        defaults.update(office_hours=office_hours)
        messages.info(request, f"Office hour updated to {office_hours}")
    officership = Officership.objects.update_or_create(
        officer=officer, semester=semester, defaults=defaults
    )

    if not is_officer(username):
        success, msg = add_officer(username)
        if success:
            messages.info(request, f"Added {username} to officers LDAP group")
        else:
            messages.error(
                request, f"Failed to add {username} to officers LDAP group: {msg}"
            )
    messages.info(request, f"{username} updated")


@staff_member_required
def update_semester(request):
    semesters = Semester.objects.all()
    return render(request, "update_semester.html", {"semesters": semesters})
