from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.db.models import Q


class UserQuerySet(models.QuerySet):
    def search_by_name(self, name):
        return self.filter(Q(name__icontains=name), is_approved=True).order_by("student_num")

    def search_by_student_num(self, student_num):
        return self.filter(Q(student_num__icontains=student_num), is_approved=True).order_by("student_num")

    def search_by_position(self, position):
        return self.filter(Q(position__icontains=position), is_approved=True).order_by("student_num")


class UserManager(BaseUserManager):
    def create_user(self, email, university, club, student_num, password, image, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)

        user = self.model(
            email=email,
            university=university,
            club=club,
            student_num=student_num,
            password=password,
            image=image,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self, email, university="PKNU", club="WAP", student_num=0, password=None, image=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, university, club, student_num, password, image, **extra_fields)

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def search_by_name(self, name):
        return self.get_queryset().search_by_name(name=name)

    def search_by_student_num(self, student_num):
        return self.get_queryset().search_by_student_num(student_num=student_num)

    def search_by_position(self, position):
        return self.get_queryset().search_by_position(position=position)
