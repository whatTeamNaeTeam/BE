from django.db import models
from django.db.models import Q, Case, When, Value, BooleanField

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
    url = models.BinaryField(null=True)
    is_approved = models.BooleanField(default=False)
    is_accomplished = models.BooleanField(default=False)


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


class LikesQuerySet(models.QuerySet):
    def team_ids(self, user_id, team_ids):
        return (
            self.filter(Q(user_id=user_id) & Q(team_id__in=team_ids))
            .values("team_id")
            .annotate(
                exists=Case(When(user_id=user_id, then=Value(True)), default=Value(False), output_field=BooleanField())
            )
        )


class LikesManager(models.Manager):
    def get_queryset(self):
        return LikesQuerySet(self.model, using=self._db)

    def team_ids(self, user_id, team_ids):
        return self.get_queryset().team_ids(user_id, team_ids)


class Likes(TimestampedModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    objects = LikesManager()


class TeamUser(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
