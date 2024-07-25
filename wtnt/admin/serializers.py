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


class AdminTeamManageDetailSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "name", "student_num", "position", "image", "image_url"]

    def get_image_url(self, obj):
        if "github" not in obj.image:
            return obj.image + "thumnail.jpg"
        else:
            return obj.image
