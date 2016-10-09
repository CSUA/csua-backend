from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Officer(models.Model):
    first_name = models.CharField(max_length = 70)
    last_name = models.CharField(max_length = 70)
    office_hours = models.CharField(max_length = 70)
    photo1_url = models.CharField(max_length = 255)
    photo2_url = models.CharField(max_length = 255)
    blurb = models.CharField(max_length = 255)
    pb_position = models.CharField(max_length = 255)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

