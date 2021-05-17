from datetime import datetime

from django.core import mail
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from apps.db_data.models import Event


def get_html_email():
    today = datetime.today()
    print(today)
    events = Event.objects.filter(date__gte=today).order_by("date")
    return render_to_string(
        "outreach/upcoming_events_email.html",
        {
            "events": events,
            "upper_left_text": "CSUA: Upcoming Events Newsletter",
            "header_image_url": "https://www.csua.berkeley.edu/static/images/pic.png",
            "small_title": "UC Berkeley Computer Science Undergraduate Association",
            "big_title": "UPCOMING EVENTS",
            "before_toc": "Announcements!",
            "preview_text": ", ".join(e.name for e in events),
            "title": "CSUA Upcoming Events",
        },
        # Old email image: "header_image_url": "https://gallery.mailchimp.com/3e2d3e62274ea01781b01bd2d/images/01a7e34b-1b9a-4625-9259-2ef05decf823.png",
    )


def index(request):
    return render(request, "outreach/index.html")


def preview(request):
    html_message = get_html_email()
    return render(request, "outreach/preview.html")


def preview_iframe(request):
    return HttpResponse(get_html_email())


def sendmail(request):
    html_message = get_html_email()
    subject = "Test Email"
    plain_message = strip_tags(html_message)
    from_email = "Robert Quitt <outreach@mail.csua.berkeley.edu>"
    to = "robertq@csua.berkeley.edu"
    mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)
    return HttpResponse("done")


def gcal(request):
    pass


"""
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    filename="", scopes=SCOPES
)
"""
