from django.db import models

from core.models import TimestampedModel
from user.models import CustomUser

# Create your models here.


class Team(TimestampedModel):
    leader = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    explain = models.CharField(max_length=100)
    genre = models.CharField(max_length=5)
    like = models.IntegerField()
    version = models.IntegerField()
    view = models.IntegerField()
    is_approved = models.BooleanField(default=False)
