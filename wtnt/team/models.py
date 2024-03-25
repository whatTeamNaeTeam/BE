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


class TeamApply(TimestampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)


class TeamTech(TimestampedModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    need_num = models.IntegerField()
    current_num = models.IntegerField()
    tech = models.CharField(max_length=15)
