from django.db import models

# Create your models here.

class Player(models.Model):
    objects = models.Manager()
    players_name = models.CharField(max_length=100)
    last_five_scores = models.CharField(max_length=200)


class okee_player_handi(models.Model):
    name = models.CharField(max_length=100)
    handicap = models.CharField(max_length=4)