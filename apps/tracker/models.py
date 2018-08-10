from time import time
from django.db import models

from apps.ldap_data.utils import uname_to_realname

# Create your models here.


def seconds_to_time(seconds: int) -> str:
    sign = "" if seconds >= 0 else "-"
    mag = abs(seconds)
    m, s = divmod(mag, 60)
    h, m = divmod(m, 60)
    return "%s%d:%02d:%02d" % (sign, h, m, s)


def currTimeMillis() -> int:
    return int(time() * 1000)


class User(models.Model):
    username = models.CharField(max_length=32, primary_key=True)
    last_ping = models.IntegerField(default=0)
    time_spent = models.IntegerField(default=0)

    @property
    def time(self):
        return seconds_to_time(self.time_spent)

    @property
    def realname(self):
        uname_to_realname(self.username)

    def update(self, delta):
        now = currTimeMillis()
        if now - self.last_ping <= 2 * 1000 * delta:
            self.time_spent += int((now - self.last_ping) / 1000)
        self.last_ping = now


class Computer(models.Model):
    hostname = models.CharField(max_length=15, primary_key=True)
    user = models.OneToOneField("User", on_delete=models.PROTECT, null=True)
    foreign_timestamp = models.IntegerField(default=0)
    local_timestamp = models.IntegerField(default=0)

    @property
    def open(self):
        return self.user.time_spent >= 7200

    @property
    def time(self):
        return seconds_to_time(self.user.time_spent)

    def update(self, user, foreign_timestamp):
        self.local_timestamp = currTimeMillis()
        self.foreign_timestamp = foreign_timestamp
        self.user = user
