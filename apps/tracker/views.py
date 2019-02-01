# Create your views here.
import base64
from datetime import datetime, timezone, timedelta
from hashlib import sha512
from json import loads
from time import time

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core import serializers

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
        if (
            computer.user is not None
            and computer.local_timestamp
            and (datetime.now(timezone.utc) - computer.local_timestamp).seconds > 5 * 60
        ):
            computer.user = None
            computer.save()

    return render(request, "computers.html", {"computers": computers, "users": users})


def json(request):
    computers = Computer.objects.all()
    users = User.objects.all()
    for computer in computers:
        if (
            computer.user is not None
            and computer.local_timestamp
            and (datetime.now(timezone.utc) - computer.local_timestamp).seconds > 5 * 60
        ):
            computer.user = None
            computer.save()

    return JsonResponse(
        {
            # "computers": list(computers.values("hostname", "user_id")),
            # "users": list(users.values("username")),
            "computers": list(computers.values()),
            "users": list(users.values()),
        }
    )


def _verify_signature(code_text, signature):
    return (
        signature.isdigit()
        and pow(int(signature), e, n)
        == int(sha512(code_text.encode("utf-8")).hexdigest(), 16) % n
    )


def ping(request, code_text=None, signature=None):
    if not _verify_signature(code_text, signature):
        print("Bad ping request.")
        return HttpResponse("Bad Request.", status=403)

    code_text = base64.b64decode(code_text).decode("utf-8")
    data = loads(code_text)
    delta = data["delta"]
    username = data["username"]
    hostname = data["host"].lower()

    # data["timestamp"] is in milliseconds since the epoch
    timestamp = datetime.fromtimestamp(int(data["timestamp"] / 1000), tz=timezone.utc)

    user, _ = User.objects.get_or_create(username=username)
    computer, computer_created = Computer.objects.get_or_create(hostname=hostname)

    # invariant: computer's foreign_timestamp is increasing each step
    if (not computer_created) and computer.foreign_timestamp >= timestamp:
        print(computer.foreign_timestamp)
        print(timestamp)
        return HttpResponse("Time went backwards!", status=403)

    now = datetime.now(tz=timezone.utc)
    # invatiant: pings from a user should come at least once every two time
    # DELTAs, but not more than once every half a DELTA. (default DELTA is 5).
    if user.last_ping and (0.5 * delta) < (now - user.last_ping).seconds < (2 * delta):
        user.time_spent += (now - user.last_ping).seconds
    user.last_ping = now
    user.save()

    computer.local_timestamp = datetime.now(tz=timezone.utc)
    computer.foreign_timestamp = timestamp
    if computer.user is not user:
        computer.user = user
    computer.save()

    return HttpResponse(str(user.time_spent))
