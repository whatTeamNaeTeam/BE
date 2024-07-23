from rest_framework import serializers
from django.contrib.auth import get_user_model

from team.models import Team

User = get_user_model()


class ApproveUserSerializer(serializers.ModelSerializer):
    is_approved = serializers.BooleanField(write_only=True)
    position = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["name", "student_num", "position", "id", "created_at", "is_approved"]


class ApproveTeamSerializer(serializers.ModelSerializer):
    is_approved = serializers.BooleanField(write_only=True)
    genre = serializers.CharField(read_only=True)

    class Meta:
        model = Team
        fields = ["id", "title", "created_at", "is_approved", "genre"]
