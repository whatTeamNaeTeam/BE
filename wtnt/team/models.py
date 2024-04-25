from django.db import models

from core.models import TimestampedModel
from user.models import CustomUser

# Create your models here.


class Team(TimestampedModel):
    leader = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, unique=True)
    explain = models.BinaryField()
    genre = models.CharField(max_length=30)
    like = models.IntegerField(default=0)
    version = models.IntegerField(default=0)
    view = models.IntegerField(default=0)
    image = models.CharField(max_length=200, null=True)
    is_approved = models.BooleanField(default=False)


class TeamApply(TimestampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    bio = models.CharField(max_length=200, default="열심히 하겠습니다!")
    tech = models.CharField(max_length=15, default="BE")
    is_approved = models.BooleanField(default=False)


class TeamTech(TimestampedModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    need_num = models.IntegerField()
    current_num = models.IntegerField(default=0)
    tech = models.CharField(max_length=15)


class TeamURL(TimestampedModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    url = models.CharField(max_length=200)


class Likes(TimestampedModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
