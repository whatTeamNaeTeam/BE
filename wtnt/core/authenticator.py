from typing import Optional, Set, TypeVar

from django.contrib.auth.models import AbstractBaseUser
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import Token
import core.exception.token as exception
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.models import TokenUser

AUTH_HEADER_TYPES = api_settings.AUTH_HEADER_TYPES

AUTH_HEADER_TYPE_BYTES: Set[bytes] = {h.encode(HTTP_HEADER_ENCODING) for h in AUTH_HEADER_TYPES}

AuthUser = TypeVar("AuthUser", AbstractBaseUser, TokenUser)


class CustomJWTAuthentication(JWTAuthentication):
    def get_raw_token(self, header: bytes) -> Optional[bytes]:
        parts = header.split()

        if len(parts) == 0:
            # Empty AUTHORIZATION header sent
            return None

        if parts[0] not in AUTH_HEADER_TYPE_BYTES:
            # Assume the header does not contain a JSON web token
            return None

        if len(parts) != 2:
            raise exception.AuthenticationHeaderSpaceError()

        return parts[1]

    def get_validated_token(self, raw_token: bytes) -> Token:
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError:
                raise exception.AccessTokenExpiredError()

    def get_user(self, validated_token: Token) -> AuthUser:
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise exception.TokenWithNoUserDataError()

        try:
            user = self.user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except self.user_model.DoesNotExist:
            raise exception.UserNotFoundInTokenDataError()

        if not user.is_active:
            raise exception.UserInactiveInTokenDataError()

        return user
