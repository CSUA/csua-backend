from django.db import models

# Create your models here.


class DiscordRegisteredUser(models.Model):
    discord_tag = models.CharField(max_length=40)
    email = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)
