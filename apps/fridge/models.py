from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=64)
    quantity = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
