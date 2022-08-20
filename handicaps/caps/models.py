from django.db import models

# Create your models here.

class player(models.Model):
    name = models.CharField(max_length=100)
    round_date = models.DateField()
    score = models.IntegerField()