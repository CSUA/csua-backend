from django.db import models

# Create your models here.


class DiscordRegisteredUser(models.Model):
    discord_tag = models.CharField(max_length=40)
    email = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)


class ConnectFourGame(models.Model):
    message_id = models.BigIntegerField(primary_key=True)
    player1 = models.BigIntegerField(help_text="Discord User ID of player 1")
    player2 = models.BigIntegerField(help_text="Discord User ID of player 2")
    is_player1_turn = models.BooleanField(default=True)
    winner = models.IntegerField(
        null=True, blank=True, help_text="Null if no winner, 1 or 2 if winner exists"
    )
    state = models.TextField()
