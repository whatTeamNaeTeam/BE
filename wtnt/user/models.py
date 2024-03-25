from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .managers import UserManager
from core.models import TimestampedModel


# Create your models here.


class CustomUser(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=5)
    university = models.CharField(max_length=8, null=True)
    club = models.CharField(max_length=10, null=True)
    student_num = models.CharField(max_length=20, null=True)
    tech = models.CharField(max_length=200, null=True)
    image = models.CharField(max_length=50, null=True)
    is_apporoved = models.BooleanField(default=False)
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
