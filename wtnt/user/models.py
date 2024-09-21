from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager
import core.exception.login as exception
from core.models import TimestampedModel


# Create your models here.


class CustomUser(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    email = models.EmailField(unique=True)
    social_id = models.IntegerField(null=True)
    name = models.CharField(max_length=12)
    university = models.CharField(max_length=8, default="부경대학교")
    club = models.CharField(max_length=10, default="WAP")
    student_num = models.CharField(max_length=12, null=True)
    position = models.CharField(max_length=15, null=True)
    explain = models.CharField(max_length=500, default="열심히 하겠습니다!")
    image = models.CharField(max_length=200, null=True)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def finish_register(self, extra_data, request_data, *args, **kwargs):
        self.student_num = str(request_data.get("student_num"))
        self.name = request_data.get("name")
        self.social_id = extra_data.get("id")
        self.email = extra_data.get("login") + "@github.com"
        self.image = extra_data.get("avatar_url")
        self.position = request_data.get("position")
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        if any(char.isdigit() or not char.isalnum() for char in self.name):
            raise exception.UserNameNotValidError()

        if not (2 <= len(self.name) <= 12):
            raise exception.UserNameTooLongError()

        if not str(self.student_num).isdigit():
            raise exception.StudentNumNotValidError()

        if not (7 <= len(str(self.student_num)) <= 10):
            raise exception.StudentNumTooLongError()

        if CustomUser.objects.filter(student_num=self.student_num).exclude(pk=self.pk).exists():
            raise exception.StudentNumDuplicatedError()

        valid_positions = ["백엔드", "프론트엔드", "AI", "디자이너"]
        if self.position not in valid_positions:
            raise exception.PositionNotValidError()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class UserUrls(models.Model):
    user = models.OneToOneField(CustomUser, primary_key=True, on_delete=models.CASCADE)
    url = models.BinaryField()


class UserTech(models.Model):
    user = models.OneToOneField(CustomUser, primary_key=True, on_delete=models.CASCADE)
    tech = models.BinaryField()
