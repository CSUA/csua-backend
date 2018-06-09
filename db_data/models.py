
import os

from django.db import models


def photo_path(instance, filename):
    # upload to MEDIA_ROOT/images/officers/{first_name}_{last_name}.{ext}
    filename, file_extension = os.path.splitext(filename)
    return 'images/officers/{0}_{1}{2}'.format(instance.first_name,
        instance.last_name, file_extension)

# Create your models here.
class Officer(models.Model):
    first_name = models.CharField(max_length = 70)
    last_name = models.CharField(max_length = 70)
    office_hours = models.CharField(max_length = 70)
    photo1 = models.ImageField(upload_to = photo_path, max_length = 255,
        default = 'images/officers/cardigan.jpg')
    photo2 = models.ImageField(upload_to = photo_path, max_length = 255,
        blank = True)
    blurb = models.CharField(max_length = 255)
    root_staff = models.BooleanField(default = False)
    tutor_subjects = models.CharField(max_length = 255, blank = True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Politburo(models.Model):
    position = models.CharField(max_length = 30)
    title = models.CharField(max_length = 30)
    description = models.CharField(max_length = 355)
    contact = models.CharField(max_length = 255)
    officer = models.OneToOneField(Officer, on_delete = models.PROTECT)

    def __str__(self):
        return self.title


def sponsor_photo_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/images/sponsors/{name}.{ext}
    filename, file_extension = os.path.splitext(filename)
    return 'images/sponsors/{0}{1}'.format(instance.name, file_extension)

class Sponsor(models.Model):
    name = models.CharField(max_length = 70)
    url = models.URLField()
    photo = models.ImageField(upload_to = sponsor_photo_path, max_length = 255,
        default = 'images/officers/cardigan.jpg')
    description = models.CharField(max_length = 255)
    current = models.BooleanField(default = True)

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length = 70)
    location = models.CharField(max_length = 70)
    date = models.DateField()
    time = models.CharField(max_length = 70)
    description = models.TextField()
    link = models.URLField()

    def __str__(self):
        return self.name
