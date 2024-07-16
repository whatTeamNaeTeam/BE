import uuid
from django.db import models

from core.models import TimestampedModel
import core.exception.team as exception
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

    def clean(self):
        if Team.objects.filter(title=self.title).exclude(pk=self.pk).exists():
            raise exception.TeamNameDuplicateError()

        if not (0 < len(self.title) <= 30):
            raise exception.TeamNameLengthError()

        valid_genres = ["웹", "앱", "게임"]
        if self.genre not in valid_genres:
            raise exception.TeamGenreNotValidError()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


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

    def clean(self):
        valid_categories = [
            "웹",
            "IOS",
            "안드로이드",
            "크로스플랫폼",
            "자바",
            "파이썬",
            "노드",
            "UI/UX 기획",
            "게임 기획",
            "컨텐츠 기획",
            "프로젝트 매니저",
            "유니티",
            "언리얼",
            "딥러닝",
            "머신러닝",
            "데이터 엔지니어",
            "게임 그래픽 디자인",
            "UI/UX 디자인",
        ]
        if self.tech not in valid_categories:
            raise exception.TeamCategoryNotValidError()

        if self.need_num and not (0 < self.need_num <= 10):
            raise exception.TeamMemberCountLengthError()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Likes(TimestampedModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    objects = LikesManager()


class TeamUser(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
