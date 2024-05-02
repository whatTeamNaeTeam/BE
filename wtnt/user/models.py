from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UserManager
from core.models import TimestampedModel


# Create your models here.


class CustomUser(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    email = models.EmailField(unique=True)
    social_id = models.IntegerField(null=True)
    name = models.CharField(max_length=5)
    university = models.CharField(max_length=8, default="부경대학교")
    club = models.CharField(max_length=10, default="WAP")
    student_num = models.CharField(max_length=20, null=True)
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


class UserUrls(models.Model):
    user = models.OneToOneField(CustomUser, primary_key=True, on_delete=models.CASCADE)
    url = models.BinaryField()


class UserTech(models.Model):
    user = models.OneToOneField(CustomUser, primary_key=True, on_delete=models.CASCADE)
    tech = models.BinaryField()
