from rest_framework.exceptions import APIException, ValidationError
from rest_framework import serializers
from rest_framework.settings import api_settings
from rest_framework.fields import get_error_detail, SkipField
from django.core.exceptions import ValidationError as DjangoValidationError
from collections.abc import Mapping

from .models import Team, TeamTech, TeamApply, Likes
from core.fields import BinaryField
import core.exception.team as exception

serializers.ValidationError


class LeaderInfoIncludedSerializer(serializers.ModelSerializer):
    leader_info = serializers.SerializerMethodField(read_only=True)

    def get_leader_info(self, obj):
        return {
            "name": obj.leader.name,
            "id": obj.leader.id,
            "image_url": obj.leader.image if "github" in obj.leader.image else obj.leader.image + "thumnail.jpg",
        }


class TeamTechCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamTech
        fields = ["id", "tech", "need_num", "current_num"]


class TeamCreateSerializer(LeaderInfoIncludedSerializer):
    category = TeamTechCreateSerializer(many=True)
    view = serializers.IntegerField(read_only=True)
    image = serializers.CharField(write_only=True)
    uuid = serializers.UUIDField(write_only=True)
    is_approved = serializers.BooleanField(read_only=True)
    leader_id = serializers.IntegerField(write_only=True)
    image_url = serializers.SerializerMethodField()
    explain = BinaryField()
    url = BinaryField(required=False, allow_null=True)

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
            "leader_id",
            "image_url",
            "image",
            "view",
            "url",
            "category",
            "uuid",
            "is_approved",
        ]

    def validate_title(self, value):
        if not (2 < len(value) <= 30):
            raise exception.TeamNameLengthError()

        if self.instance and self.instance.pk:
            if Team.objects.filter(title=value).exclude(pk=self.instance.pk).exists():
                raise exception.TeamNameDuplicateError()
        else:
            if Team.objects.filter(title=value).exists():
                raise exception.TeamNameDuplicateError()

        return value

    def validate_genre(self, value):
        valid_genres = ["웹", "안드로이드", "IOS", "크로스플랫폼", "게임", "기타"]
        if value not in valid_genres:
            raise exception.TeamGenreNotValidError()

        return value

    def validate_explain(self, value):
        if value is not None and not (0 < len(value) <= 2000):
            raise exception.TeamExplainLengthError()

        return value

    def validate_url(self, value):
        print(value)
        if value is not None and len(value) == 0:
            raise exception.TeamUrlLengthError()

    def get_image_url(self, obj):
        if obj.image is None:
            return None
        else:
            # 나중에 이미지 여러장을 지원하기 위해
            image_url = obj.image + "image.jpg"
            return [image_url]

    def to_internal_value(self, data):
        """
        Dict of native values <- Dict of primitive datatypes.
        """
        if not isinstance(data, Mapping):
            message = self.error_messages["invalid"].format(datatype=type(data).__name__)
            raise ValidationError({api_settings.NON_FIELD_ERRORS_KEY: [message]}, code="invalid")

        ret = {}
        errors = {}
        fields = self._writable_fields

        for field in fields:
            validate_method = getattr(self, "validate_" + field.field_name, None)
            primitive_value = field.get_value(data)
            try:
                if validate_method is not None:
                    validated_value = validate_method(primitive_value)
                validated_value = field.run_validation(primitive_value)
            except APIException as api_exception:
                raise api_exception
            except ValidationError as exc:
                errors[field.field_name] = exc.detail
            except DjangoValidationError as exc:
                errors[field.field_name] = get_error_detail(exc)
            except SkipField:
                pass
            else:
                self.set_value(ret, field.source_attrs, validated_value)

        if errors:
            raise ValidationError(errors)

        return ret

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
    user_id = serializers.IntegerField(write_only=True)
    user_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TeamApply
        fields = ["id", "team_id", "user_id", "created_at", "bio", "tech", "user_info"]

    def get_user_info(self, obj):
        return {
            "id": obj.user.id,
            "name": obj.user.name,
            "image_url": obj.user.image + "thumnail.jpg",
            "position": obj.user.position,
        }


class TeamListSerializer(LeaderInfoIncludedSerializer):
    category = TeamTechCreateSerializer(many=True, read_only=True)
    image = serializers.CharField(write_only=True)
    is_approved = serializers.BooleanField(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            "id",
            "title",
            "image",
            "image_url",
            "category",
            "leader_info",
            "like",
            "version",
            "view",
            "genre",
            "is_approved",
        ]

    def get_image_url(self, obj):
        if obj.image is None:
            return None
        return obj.image + "thumnail.jpg"


class TeamLikeSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Likes
        fields = ["user_id", "team_id"]


class TeamManageActivitySerializer(LeaderInfoIncludedSerializer):
    class Meta:
        model = Team
        fields = ["id", "title", "leader_info"]
