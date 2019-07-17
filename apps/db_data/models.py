import os
import datetime

from django.db import models
from django.contrib.auth.models import User as DjangoUser


class Semester(models.Model):
    id = models.CharField(max_length=8, primary_key=True)
    current = models.BooleanField()
    name = models.CharField(max_length=16)
    officers = models.ManyToManyField("Officer", through="Officership", blank=True)
    politburo = models.ManyToManyField("Politburo", through="PolitburoMembership")
    sponsors = models.ManyToManyField("Sponsor", through="Sponsorship")
    events = models.ManyToManyField("Event", blank=True)

    def __str__(self):
        return self.name


def person_photo_path(instance, filename):
    # upload to MEDIA_ROOT/images/people/{first_name}_{last_name}_alt.{ext}
    filename, file_extension = os.path.splitext(filename)
    return "images/people/{0}_{1}{2}".format(
        instance.user.first_name, instance.user.last_name, file_extension
    )


def person_photo_path_alt(instance, filename):
    filename, file_extension = os.path.splitext(filename)
    return "images/people/{0}_{1}_alt{2}".format(
        instance.user.first_name, instance.user.last_name, file_extension
    )


class Person(models.Model):
    user = models.OneToOneField(
        DjangoUser, on_delete=models.PROTECT, primary_key=True, to_field="username"
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
        return str(self.user)


# Create your models here.
class Officer(models.Model):
    person = models.OneToOneField(Person, on_delete=models.PROTECT, unique=True)
    root_staff = models.BooleanField(default=False)
    officer_since = models.DateField()

    def __str__(self):
        return str(self.person)

    @property
    def is_anniversary(self):
        today = datetime.date.today()
        return (
            self.officer_since.month == today.month
            and self.officer_since.day == today.day
        )


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
        return self.title


class PolitburoMembership(models.Model):
    politburo = models.ForeignKey(Politburo, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.PROTECT)

    @property
    def contact_info(self):
        return self.politburo.contact.replace("[name]", self.person.user.first_name, 1)

    def __str__(self):
        return str(self.semester) + ": " + str(self.politburo) + ": " + str(self.person)


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
    date = models.DateField(null=True)
    time = models.CharField(max_length=70)
    description = models.TextField()
    link = models.URLField(blank=True)
    category = models.ForeignKey("EventCategory", null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    @property
    def is_passed(self):
        return self.date < datetime.date.today()


class EventCategory(models.Model):
    id = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=32)
