from __future__ import unicode_literals
import os

from django.db import models

def photo_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/images/officers/{first_name}_{last_name}.jpg
    filename, file_extension = os.path.splitext(filename)
    return 'images/officers/{0}_{1}{2}'.format(instance.first_name, instance.last_name, file_extension)

# Create your models here.
class Officer(models.Model):
    first_name = models.CharField(max_length = 70)
    last_name = models.CharField(max_length = 70)
    office_hours = models.CharField(max_length = 70)
    photo1 = models.ImageField(upload_to = photo_path, max_length = 255, default = 'images/officers/cardigan.jpg')
    photo2 = models.ImageField(upload_to = photo_path, max_length = 255, blank = True)
    blurb = models.CharField(max_length = 255)
    pb_position = models.CharField(max_length = 255, blank = True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

