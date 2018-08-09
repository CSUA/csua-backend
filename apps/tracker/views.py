# Create your views here.
import base64
from datetime import datetime
from hashlib import sha512
from json import loads
from time import time

from django.http import HttpResponse
from django.shortcuts import render

n = 24758167959654528007156374531915464081839760935532218683689708649238085888673119
e = 1792365660034190580552551249494619970913188709474773556763388672115404129751573

userdb = {}
hostdb = {}
DAILY_QUOTA = 3600 * 2
lastreset = datetime.today().day
needsReset = True

twitchUsers = {
    "jaze": "alxjaze",
    "jonathanjtan": "dragaanwawa",
    "nlingarkar": "sirnellington",
}


def currTimeMillis() -> int:
    return int(time() * 1000)


def seconds_to_time(seconds: int) -> str:
    sign = "" if seconds >= 0 else "-"
    mag = abs(seconds)
    m, s = divmod(mag, 60)
    h, m = divmod(m, 60)
    return "%s%d:%02d:%02d" % (sign, h, m, s)


def resetAccounts() -> None:
    global lastreset
    global needsReset
    if datetime.today().weekday() == 0 and needsReset:
        needsReset = False
        lastreset = datetime.today().day
        for user in userdb.values():
            user.timeSpent = 0
    elif datetime.today().weekday() != 0:
        needsReset = True


class User:
    def __init__(self, username: str):
        self.username = username
        self.last_ping = currTimeMillis()
        self.time_spent = 0

    @property
    def time(self):
        return seconds_to_time(self.time_spent)

    def update(self, delta):
        now = currTimeMillis()
        if now - self.last_ping <= 2 * 1000 * delta:
            self.time_spent += int((now - self.last_ping) / 1000)
        self.last_ping = now


class Computer:
    def __init__(self, hostname):
        self.hostname = hostname
        self.user = ""
        self.foreign_timestamp = 0
        self.local_timestamp = 0

    @property
    def twitchUser(self):
        return None if self.user not in twitchUsers else twitchUsers[self.user]

    @property
    def open(self):
        return self.user.time_spent >= 7200

    @property
    def time(self):
        return seconds_to_time(self.user.time_spent)

    def update(self, user, foreign_timestamp, local_timestamp):
        self.local_timestamp = local_timestamp
        self.foreign_timestamp = foreign_timestamp
        self.user = user


def getComputers():
    resetAccounts()
    out = []
    for computer in hostdb.values():
        timestamp = computer.local_timestamp
        if (currTimeMillis() - timestamp) < 10000:
            out.append(computer)
        # else:
        #     # out.append(Computer(host, True, "N/A", -1))
    return out


def index(request):
    computers = getComputers()
    print(computers)
    users = userdb.values()
    print(users)
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
    resetAccounts()
    data = loads(code_text)
    delta = data["delta"]
    username = data["username"]
    hostname = data["host"].lower()
    timestamp = data["timestamp"]
    if hostname in hostdb:
        computer = hostdb[hostname]
        if computer.foreign_timestamp >= timestamp:
            return HttpResponse("Bad Request, stupid hacker.", status=403)
        computer.update(
            user=userdb[username],
            foreign_timestamp=timestamp,
            local_timestamp=currTimeMillis(),
        )
    else:
        hostdb[hostname] = Computer(hostname)

    if username not in userdb:
        userdb[username] = User(username=username)
    user = userdb[username]
    user.update(delta)
    return HttpResponse(str(user.time_spent))
