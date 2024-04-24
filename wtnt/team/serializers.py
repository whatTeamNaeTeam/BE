from rest_framework import serializers
from .models import Team, TeamURL, TeamTech


class MyBinaryField(serializers.Field):
    def to_representation(self, value):
        return value.decode("utf-8")

    def to_internal_value(self, data):
        return data.encode("utf-8")


class TeamCreateSerializer(serializers.ModelSerializer):
    leader_id = serializers.IntegerField()
    explain = MyBinaryField()

    class Meta:
        model = Team
        fields = ["id", "leader_id", "name", "explain", "genre", "like", "version", "image"]


class TeamUrlCreateSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField()

    class Meta:
        model = TeamURL
        fields = ["id", "team_id", "url"]


class TeamTechCreateSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField()

    class Meta:
        model = TeamTech
        fields = ["id", "team_id", "tech", "need_num", "current_num"]
