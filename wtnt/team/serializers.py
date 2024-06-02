from rest_framework import serializers
from .models import Team, TeamTech, TeamApply, Likes
from core.fields import BinaryField


class TeamTechCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamTech
        fields = ["id", "tech", "need_num", "current_num"]


class TeamCreateSerializer(serializers.ModelSerializer):
    category = TeamTechCreateSerializer(many=True)
    view = serializers.CharField(read_only=True)
    image = serializers.CharField(write_only=True)
    image_url = serializers.SerializerMethodField()
    leader_info = serializers.SerializerMethodField(read_only=True)
    explain = BinaryField()
    url = BinaryField()

    class Meta:
        model = Team
        fields = [
            "id",
            "leader_info",
            "title",
            "explain",
            "genre",
            "like",
            "version",
            "image_url",
            "image",
            "view",
            "url",
            "category",
        ]

    def get_leader_info(self, obj):
        return {"name": obj.leader.name, "id": obj.leader.id, "image_url": obj.leader.image + "thumnail.jpg"}

    def get_image_url(self, obj):
        return obj.image + "image.jpg"

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
    leader_info = serializers.SerializerMethodField(read_only=True)
    image = serializers.CharField(write_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ["id", "title", "image", "image_url", "category", "leader_info", "like", "version", "view", "genre"]

    def get_leader_info(self, obj):
        return {"id": obj.leader.id, "name": obj.leader.name, "image_url": obj.leader.image + "thumnail.jpg"}

    def get_image_url(self, obj):
        return obj.image + "thumnail.jpg"


class TeamLikeSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Likes
        fields = ["user_id", "team_id"]


class TeamManageActivitySerializer(serializers.ModelSerializer):
    leader_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Team
        fields = ["id", "title", "leader_info"]

    def get_leader_info(self, obj):
        return {"id": obj.leader.id, "name": obj.leader.name, "image_url": obj.leader.image + "thumnail.jpg"}
