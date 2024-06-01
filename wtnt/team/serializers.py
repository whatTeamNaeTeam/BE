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
    view = serializers.CharField(read_only=True)
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
            "view",
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

    def update(self, instance, validated_data):
        techs = validated_data.pop("category", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if techs is not None:
            existing_techs = {tech.tech: tech for tech in instance.category.all()}

            for tech in techs:
                tech_name = tech.get("tech")
                if tech_name and tech_name in existing_techs:
                    tech_instance = existing_techs.pop(tech_name)
                    for attr, value in tech.items():
                        setattr(tech_instance, attr, value)
                    tech_instance.save()
                else:
                    TeamTech.objects.create(team=instance, **tech)
            for tech_instance in existing_techs.values():
                tech_instance.delete()

        return instance


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


class TeamManageActivitySerializer(serializers.ModelSerializer):
    leader_id = serializers.SerializerMethodField(read_only=True)
    leader_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Team
        fields = ["id", "name", "leader_name", "leader_id"]

    def get_leader_name(self, obj):
        return obj.leader.name

    def get_leader_id(self, obj):
        return obj.leader.id
