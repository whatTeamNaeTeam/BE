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
    image_url = serializers.SerializerMethodField()
    image = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = BaseUserSerializer.Meta.fields + ["image", "image_url"]

    def get_image_url(self, obj):
        if "github" not in obj.image:
            return obj.image + "image.jpg"
        else:
            return obj.image


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


class UserSerializerOnTeamManageDetail(BaseUserSerializer):
    image_url = serializers.SerializerMethodField()
    image = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ["position", "image_url", "image"]

    def get_image_url(self, obj):
        if "github" not in obj.image:
            return obj.image + "thumnail.jpg"
        else:
            return obj.image
