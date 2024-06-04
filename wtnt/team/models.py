import uuid
from django.db import models

from core.models import TimestampedModel
from user.models import CustomUser
from .manager import LikesManager, TeamManager

# Create your models here.


class Team(TimestampedModel):
    leader = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=30, unique=True)
    explain = models.BinaryField()
    genre = models.CharField(max_length=30)
    like = models.IntegerField(default=0)
    version = models.IntegerField(default=0)
    view = models.IntegerField(default=0)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    image = models.CharField(max_length=200, null=True)
    url = models.BinaryField(null=True)
    is_approved = models.BooleanField(default=False)
    is_accomplished = models.BooleanField(default=False)
    objects = TeamManager()


class TeamApply(TimestampedModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    bio = models.CharField(max_length=200, default="열심히 하겠습니다!")
    tech = models.CharField(max_length=15, default="BE")
    is_approved = models.BooleanField(default=False)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "team", "tech"], name="teamapply_unique")]


class TeamTech(TimestampedModel):
    team = models.ForeignKey(Team, related_name="category", on_delete=models.CASCADE)
    need_num = models.IntegerField()
    current_num = models.IntegerField(default=0)
    tech = models.CharField(max_length=15)


class Likes(TimestampedModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    objects = LikesManager()


class TeamUser(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
