from datetime import datetime

from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.http import HttpResponse
from django.shortcuts import render

from apps.db_data.models import Event


def get_html_email():
    today = datetime.today()
    print(today)
    events = Event.objects.filter(date__gte=today)
    return render_to_string("outreach/upcoming_events_email.html", {"events": events})


def index(request):
    return render(request, "outreach/index.html")


def preview(request):
    html_message = get_html_email()
    # return render(request, "outreach/preview.html", {"html_message": html_message})
    return render(request, "outreach/preview.html")
    # return HttpResponse(get_html_email())


def preview_iframe(request):
    return HttpResponse(get_html_email())


def sendmail(request):
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
