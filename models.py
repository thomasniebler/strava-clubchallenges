from django.db import models

from stravauth.models import StravaToken


class Challenge(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    goal_distance = models.FloatField()
    club = models.CharField(max_length=200)
    participant = models.ForeignKey(StravaToken, on_delete=models.CASCADE)
