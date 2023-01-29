from django.db import models

# Create your models here.

class okee_Player(models.Model):
    objects = models.Manager()
    players_name = models.CharField(max_length=100)
    last_five_scores = models.CharField(max_length=200)


class delray_Player(models.Model):
    objects = models.Manager()
    players_name = models.CharField(max_length=100)
    last_five_scores = models.CharField(max_length=200)


class commons_Player(models.Model):
    objects = models.Manager()
    players_name = models.CharField(max_length=100)
    last_five_scores = models.CharField(max_length=200)


class dreher_Player(models.Model):
    objects = models.Manager()
    players_name = models.CharField(max_length=100)
    last_five_scores = models.CharField(max_length=200)


class pga_Player(models.Model):
    objects = models.Manager()
    players_name = models.CharField(max_length=100)
    last_five_scores = models.CharField(max_length=200)


