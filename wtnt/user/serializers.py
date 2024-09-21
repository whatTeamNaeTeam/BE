from rest_framework.exceptions import APIException, ValidationError
from rest_framework import serializers
from rest_framework.settings import api_settings
from rest_framework.fields import get_error_detail, SkipField
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model
from collections.abc import Mapping
from user.models import UserTech, UserUrls
from core.fields import BinaryField
from core.exception.login import UserExplainTooLong

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

    def validate_explain(self, value):
        if len(value) > 500:
            raise UserExplainTooLong()

        return value

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
