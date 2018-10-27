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


class User(models.Model):
    username = models.CharField(max_length=32, primary_key=True)
    last_ping = models.DateTimeField(auto_now_add=True)
    time_spent = models.IntegerField(default=0)

    @property
    def time(self):
        return seconds_to_time(self.time_spent)

    @property
    def realname(self):
        return uname_to_realname(self.username)


class Computer(models.Model):
    hostname = models.CharField(max_length=15, primary_key=True)
    user = models.OneToOneField("User", on_delete=models.PROTECT, null=True)
    foreign_timestamp = models.DateTimeField(auto_now_add=True)
    local_timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def open(self):
        return self.user.time_spent >= 7200

    @property
    def time(self):
        return seconds_to_time(self.user.time_spent)
