import datetime
import os

import pytz
from django.contrib.auth.models import User as DjangoUser
from django.db import models


class Semester(models.Model):
    id = models.CharField(
        max_length=8,
        primary_key=True,
        help_text="Used for URLs, should match /(fa|sp)[0-9]{2}/",
    )
    current = models.BooleanField(
        help_text="There should only be one current semester."
    )
    name = models.CharField(max_length=16, help_text="Display name")
    officers = models.ManyToManyField("Officer", through="Officership", blank=True)
    politburo = models.ManyToManyField("Politburo", through="PolitburoMembership")
    sponsors = models.ManyToManyField("Sponsor", through="Sponsorship")
    events = models.ManyToManyField("Event", blank=True, help_text="Currently unused.")

    def __str__(self):
        return self.name


def person_photo_path(instance, filename):
    filename, file_extension = os.path.splitext(filename)
    return "images/people/{0}_{1}{2}".format(
        instance.user.first_name, instance.user.last_name, file_extension
    )


def person_photo_path_alt(instance, filename):
    filename, file_extension = os.path.splitext(filename)
    return "images/people/{0}_{1}_alt{2}".format(
        instance.user.first_name, instance.user.last_name, file_extension
    )


PERSON_HELP_TEXT = (
    "There is one Officer object<->one Person object<->one auth.User<->one LDAP user"
)


class Person(models.Model):
    user = models.OneToOneField(
        DjangoUser,
        on_delete=models.PROTECT,
        primary_key=True,
        to_field="username",
        help_text=PERSON_HELP_TEXT,
    )
    photo1 = models.ImageField(
        upload_to=person_photo_path,
        max_length=255,
        default="images/officers/cardigan.jpg",
    )
    photo2 = models.ImageField(
        upload_to=person_photo_path_alt, max_length=255, blank=True
    )
    video2 = models.FileField(
        upload_to=person_photo_path_alt, max_length=255, blank=True
    )

    def __str__(self):
        return f"{self.user!s} ({self.user.first_name} {self.user.last_name})"

    @property
    def username(self):
        return self.user.username


# Create your models here.
class Officer(models.Model):
    person = models.OneToOneField(
        Person, on_delete=models.PROTECT, unique=True, help_text=PERSON_HELP_TEXT
    )
    root_staff = models.BooleanField(default=False)
    officer_since = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.person)

    @property
    def is_anniversary(self):
        today = datetime.date.today()
        return self.officer_since and (
            self.officer_since.month == today.month
            and self.officer_since.day == today.day
        )

    @property
    def username(self):
        return self.person.username


class Officership(models.Model):
    officer = models.ForeignKey(Officer, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    tutor_subjects = models.ManyToManyField("UcbClass", blank=True)
    blurb = models.CharField(max_length=255)
    office_hours = models.CharField(max_length=70)

    def __str__(self):
        return str(self.semester) + ": " + str(self.officer)

    @property
    def is_tutor(self):
        return len(self.tutor_subjects.all()) > 0


class UcbClass(models.Model):
    id = models.CharField(max_length=8, primary_key=True)

    def __str__(self):
        return self.id


class Politburo(models.Model):
    position = models.CharField(max_length=30)
    title = models.CharField(max_length=30)
    description = models.TextField()
    contact = models.TextField(max_length=255)

    def __str__(self):
        return f"{self.position} ({self.title})"


class PolitburoMembership(models.Model):
    politburo = models.ForeignKey(Politburo, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)

    @property
    def contact_info(self):
        return self.politburo.contact.replace("[name]", self.person.user.first_name, 1)

    def __str__(self):
        return f"{self.semester}: {self.politburo.position}: {self.person.user}"


def sponsor_photo_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/images/sponsors/{name}.{ext}
    filename, file_extension = os.path.splitext(filename)
    return "images/sponsors/{0}{1}".format(instance.name, file_extension)


class Sponsor(models.Model):
    name = models.CharField(max_length=70)
    url = models.URLField()
    photo = models.ImageField(
        upload_to=sponsor_photo_path,
        max_length=255,
        default="images/officers/cardigan.jpg",
    )

    def __str__(self):
        return self.name


class Sponsorship(models.Model):
    sponsor = models.ForeignKey(Sponsor, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)


class Event(models.Model):
    name = models.CharField(max_length=70)
    location = models.CharField(max_length=70)
    date_time = models.DateTimeField(null=False)
    description = models.TextField()
    link = models.URLField(blank=True)
    category = models.ForeignKey(
        "EventCategory",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        help_text="Currently unused.",
    )
    ordering = ["date_time"]

    @property
    def is_passed(self):
        return self.date_time < pytz.timezone.now()

    def get_time_string(self):
        return self.date_time.astimezone(pytz.timezone("US/Pacific")).strftime(
            "%I:%M %p %Z"
        )

    def get_date_string(self):
        return self.date_time.astimezone(pytz.timezone("US/Pacific")).strftime("%x")

    def __str__(self):
        if not self.date_time:
            return f"{self.name}"
        return f"{self.name} ({self.get_date_string()})"


class EventCategory(models.Model):
    id = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=32)


class Notice(models.Model):
    text = models.TextField(help_text="Markdown for the text of the notice")
    expires = models.DateField()
