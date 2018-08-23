from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .models import Event, Officer, Politburo, Sponsor

from fiber.models import Page


# Create your views here.
def officers(request):
    officer_list = Officer.objects.filter(enabled=True)
    fiber_page = Page.objects.get(title__exact="Officers")
    return render(
        request,
        fiber_page.template_name,
        {"officer_list": officer_list, "fiber_page": fiber_page},
    )


def politburo(request):
    pb = Politburo.objects.all()
    for member in pb:
        member.contact = member.contact.replace("[name]", member.officer.first_name)
    fiber_page = Page.objects.get(title__exact="Politburo")
    return render(request, "politburo.html", {"pb": pb, "fiber_page": fiber_page})

def events(request):
    events = Event.objects.all()
    fiber_page = Page.objects.get(title__exact="Events")
    return render(request, "events.html", {"events": events, "fiber_page": fiber_page})


def sponsors(request):
    sponsors_all = Sponsor.objects.order_by("name")

    sponsors_current = []
    sponsors_old = []
    count_current = 0
    count_old = 0
    for sponsor in sponsors_all:
        if sponsor.current:
            if count_current % 4 == 0:
                sponsors_current.append([])
            sponsors_current[count_current // 4].append(sponsor)
            count_current += 1
        else:
            if count_old % 4 == 0:
                sponsors_old.append([])
            sponsors_old[count_old // 4].append(sponsor)
            count_old += 1

    fiber_page = Page.objects.get(title__exact="Sponsors")
    return render(
        request,
        fiber_page.template_name,
        {"sponsors_current": sponsors_current, "sponsors_old": sponsors_old, "fiber_page": fiber_page},
    )


def json(request):
    officers_all = Officer.objects.filter(enabled=True).order_by("last_name")
    serialized_officers = [
        {
            "name": o.first_name + " " + o.last_name,
            "hours": o.office_hours,
            "img": o.photo1.url if o.photo1 else None,
            "img2": o.photo2.url if o.photo2 else None,
            "quote": o.blurb,
            "rootStaff": o.root_staff,
            "tutorSubjects": o.tutor_subjects,
        }
        for o in officers_all
    ]

    pb_arr = Politburo.objects.all()
    pb_dict = {}
    for pb_member in pb_arr:
        pb_dict[pb_member.position] = {
            "name": pb_member.officer.first_name + " " + pb_member.officer.last_name,
            "img": pb_member.officer.photo1.url if pb_member.officer.photo1 else None,
        }

    events_all = Event.objects.order_by("date")
    serialized_events = [
        {
            "name": e.name,
            "location": e.location,
            "date": e.date.strftime("%A - %m/%d"),
            "time": e.time,
            "description": e.description,
            "href": e.link,
        }
        for e in events_all
    ]

    sponsors_all = Sponsor.objects.order_by("name")
    serialized_sponsors = [
        {
            "name": s.name,
            "href": s.url,
            "type": s.description,
            "img": s.photo.url if s.photo else None,
            "current": s.current,
        }
        for s in sponsors_all
    ]

    result = {
        "officers": serialized_officers,
        "pb": pb_dict,
        "events": serialized_events,
        "sponsors": serialized_sponsors,
    }
    return JsonResponse(result)
