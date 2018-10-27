# Create your views here.
import base64
from datetime import datetime, timezone
from hashlib import sha512
from json import loads
from time import time

from django.http import HttpResponse
from django.shortcuts import render

from .models import User, Computer

n = 24758167959654528007156374531915464081839760935532218683689708649238085888673119
e = 1792365660034190580552551249494619970913188709474773556763388672115404129751573

DAILY_QUOTA = 3600 * 2

twitchUsers = {
    "jaze": "alxjaze",
    "jonathanjtan": "dragaanwawa",
    "nlingarkar": "sirnellington",
}

def index(request):
    computers = Computer.objects.all()
    users = User.objects.all()
    for computer in computers:
        if computer.user is not None and computer.local_timestamp and (datetime.now(timezone.utc) - computer.local_timestamp).seconds > 5 * 60:
            computer.user = None
            computer.save()

    return render(request, "computers.html", {"computers": computers, "users": users})


def verify_signature(code_text, signature):
    return (
        signature.isdigit()
        and pow(int(signature), e, n)
        == int(sha512(code_text.encode("utf-8")).hexdigest(), 16) % n
    )

def ping(request, code_text=None, signature=None):
    if not verify_signature(code_text, signature):
        return HttpResponse("Bad Request.", status=403)

    code_text = base64.b64decode(code_text).decode("utf-8")
    data = loads(code_text)
    delta = data["delta"]
    username = data["username"]
    hostname = data["host"].lower()
    timestamp = datetime.fromtimestamp(int(data["timestamp"] / 1000))

    user, _ = User.objects.get_or_create(username=username)
    computer, _ = Computer.objects.get_or_create(hostname=hostname)

    if computer.foreign_timestamp and computer.foreign_timestamp >= timestamp:
        return HttpResponse("Bad Request, stupid hacker.", status=403)

    now = datetime.now(timezone.utc)
    if user.last_ping and now - user.last_ping < 10 * delta:
        user.time_spent += now - user.last_ping
    user.last_ping = now
    user.save()

    computer.local_timestamp = datetime.now(timezone.utc)
    computer.foreign_timestamp = timestamp
    computer.user = user
    computer.save()

    return HttpResponse(str(user.time_spent))
