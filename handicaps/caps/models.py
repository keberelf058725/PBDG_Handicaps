from django.db import models

# Create your models here.

class player(models.Model):
    name = models.CharField(max_length=100)
    score = models.CharField(max_length=200)
    handicap = models.CharField(max_length=4)