from rest_framework import serializers
from django.contrib.auth import get_user_model
from user.models import UserTech, UserUrls
from core.fields import BinaryField

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["name", "student_num", "id"]


class UserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = BaseUserSerializer.Meta.fields + ["image"]


class UserProfileSerializer(UserSerializer):
    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ["is_approved", "is_staff", "position", "explain"]


class UserUrlSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    url = BinaryField()

    class Meta:
        model = UserUrls
        fields = ["url", "user_id"]


class UserTechSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    tech = BinaryField()

    class Meta:
        model = UserTech
        fields = ["tech", "user_id"]
