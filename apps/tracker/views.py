# Create your views here.
import base64
from datetime import datetime
from hashlib import sha512
from json import loads
from time import time

from django.http import HttpResponse
from django.shortcuts import render

from .models import User, Computer

n = 24758167959654528007156374531915464081839760935532218683689708649238085888673119
e = 1792365660034190580552551249494619970913188709474773556763388672115404129751573

DAILY_QUOTA = 3600 * 2
lastreset = datetime.today().day
needsReset = True

twitchUsers = {
    "jaze": "alxjaze",
    "jonathanjtan": "dragaanwawa",
    "nlingarkar": "sirnellington",
}


def resetAccounts() -> None:
    global lastreset
    global needsReset
    if datetime.today().weekday() == 0 and needsReset:
        needsReset = False
        lastreset = datetime.today().day
        for user in User.objects.all():
            user.time_spent = 0
    elif datetime.today().weekday() != 0:
        needsReset = True


def getComputers():
    resetAccounts()
    out = []
    for computer in Computer.objects.all():
        timestamp = computer.local_timestamp
        # if (currTimeMillis() - timestamp) < 10000:
        out.append(computer)
        # else:
        #     out.append(Computer(host, True, "N/A", -1))
    return out


def index(request):
    computers = getComputers()
    users = User.objects.all()
    return render(request, "computers.html", {"computers": computers, "users": users})


def verify_signature(code_text, signature):
    return (
        signature.isdigit()
        and pow(int(signature), e, n)
        == int(sha512(code_text.encode("utf-8")).hexdigest(), 16) % n
    )


def currTimeMillis() -> int:
    return int(time() * 1000)


def ping(request, code_text=None, signature=None):
    if not verify_signature(code_text, signature):
        return HttpResponse("Bad Request.", status=403)
    code_text = base64.b64decode(code_text).decode("utf-8")
    resetAccounts()
    data = loads(code_text)
    delta = data["delta"]
    username = data["username"]
    hostname = data["host"].lower()
    timestamp = data["timestamp"]

    user, _ = User.objects.get_or_create(username=username)
    computer, _ = Computer.objects.get_or_create(hostname=hostname)

    if computer.foreign_timestamp >= timestamp:
        return HttpResponse("Bad Request, stupid hacker.", status=403)

    now = currTimeMillis()
    if now - user.last_ping <= 2 * 1000 * delta:
        user.time_spent += int((now - user.last_ping) / 1000)
    user.last_ping = now
    user.save()

    computer.local_timestamp = currTimeMillis()
    computer.foreign_timestamp = timestamp
    computer.user = user
    computer.save()

    return HttpResponse(str(user.time_spent))
