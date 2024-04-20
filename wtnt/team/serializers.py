from rest_framework import serializers
from .models import Team


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
        fields = ["leader_id", "name", "explain", "genre", "like", "version", "image"]
