from rest_framework import serializers
from .models import Team, TeamTech, TeamApply, Likes
from core.fields import BinaryField


class TeamTechCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamTech
        fields = ["id", "tech", "need_num", "current_num"]


class TeamCreateSerializer(serializers.ModelSerializer):
    category = TeamTechCreateSerializer(many=True)
    leader_id = serializers.IntegerField()
    leader_name = serializers.SerializerMethodField(read_only=True)
    explain = BinaryField()
    url = BinaryField()

    class Meta:
        model = Team
        fields = [
            "id",
            "leader_id",
            "leader_name",
            "name",
            "explain",
            "genre",
            "like",
            "version",
            "image",
            "url",
            "category",
        ]

    def get_leader_name(self, obj):
        return obj.leader.name

    def create(self, validated_data):
        techs = validated_data.pop("category")
        team = Team.objects.create(**validated_data)

        for tech in techs:
            TeamTech.objects.create(team=team, **tech)

        return team


class TeamApplySerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    is_approved = serializers.BooleanField(write_only=True)

    class Meta:
        model = TeamApply
        fields = ["id", "team_id", "user_id", "is_approved", "created_at", "bio", "tech"]


class TeamListSerializer(serializers.ModelSerializer):
    category = TeamTechCreateSerializer(many=True, read_only=True)
    leader_name = serializers.SerializerMethodField()
    leader_id = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ["id", "name", "image", "category", "leader_id", "leader_name", "like", "version", "view", "genre"]

    def get_leader_name(self, obj):
        return obj.leader.name

    def get_leader_id(self, obj):
        return obj.leader.id


class TeamLikeSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Likes
        fields = ["user_id", "team_id"]
