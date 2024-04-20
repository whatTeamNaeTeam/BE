from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["name", "student_num", "id"]


class UserSerializer(BaseUserSerializer):
    class Meta:
        model = User
        fields = BaseUserSerializer.Meta.fields + ["image"]


class ApproveUserSerializer(BaseUserSerializer):
    is_approved = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = BaseUserSerializer.Meta.fields + ["is_approved"]