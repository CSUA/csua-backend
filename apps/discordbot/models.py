from django.db import models

# Create your models here.


class DiscordRegisteredUser(models.Model):
    discord_tag = models.CharField(max_length=40)
    email = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)


class ConnectFourGame(models.Model):
    message_id = models.IntegerField(primary_key=True)
    player1 = models.IntegerField()
    player2 = models.IntegerField()
    is_player1_turn = models.BooleanField(default=True)
    winner = models.IntegerField(null=True, blank=True)
    state = models.CharField(max_length=255)
