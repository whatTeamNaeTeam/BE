from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from core.utils.auth import get_user_info
from core.utils.redis import RedisUtils
from core.service import BaseService
from core.exceptions import CodeNotMatchError, RefreshTokenExpiredError, CeleryTaskError
from user.tasks import send_email

User = get_user_model()


class AuthService(BaseService):
    def determine_callback_url(self):
        is_web = self.request.META.get("HTTP_X_FROM", None)
        if is_web == "web":
            return "https://local.whatmeow.shop:3001/oauth/callback/github"
        elif is_web == "app":
            return "myapp://auth"
        else:
            return "http://localhost:8000/api/auth/github/callback"

    def process_response_data(self, response_data):
        refresh_token = response_data.get("refresh", None)
        access_token = response_data.get("access", None)
        user_id = response_data["user"]["pk"]

        if refresh_token:
            RedisUtils.set_refresh_token(user_id, refresh_token)
            response_data.pop("refresh")

        _, email = response_data["user"]["email"].split("@")
        response_data.pop("user")

        if "sample.com" in email:
            response_data["registered"] = False
        else:
            response_data["registered"] = True
            user = User.objects.get(id=user_id)
            response_data["user"] = get_user_info(user)

        response_data.pop("access")
        return response_data, access_token


class RegisterService(BaseService):
    def finish_register_by_user_input(self):
        code = self.request.data.get("code")
        email = self.request.data.get("email")

        if code != RedisUtils.get_code_in_redis_from_email(email):
            raise CodeNotMatchError()

        extra_data = SocialAccount.objects.get(user_id=self.request.user.id).extra_data
        user = User.objects.get(id=self.request.user.id)
        user.finish_register(extra_data=extra_data, request_data=self.request.data)

        RedisUtils.delete_code_in_redis_from_email(email)

        return user


class RefreshService(BaseService):
    def extract_refresh_token(self):
        _, access_token = self.request.META.get("HTTP_AUTHORIZATION").split(" ")
        user_id = AccessToken(access_token, verify=False).payload.get("user_id")

        refresh_token = RedisUtils.get_refresh_token(user_id)
        if not refresh_token:
            raise RefreshTokenExpiredError()

        return refresh_token

    def get_new_access_token_from_serializer(self, serializer):
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        token = serializer.validated_data

        return token


class EmailVerifyService(BaseService):
    def send_email(self):
        email = self.request.data.get("email")

        try:
            send_email.delay(email)
        except Exception as e:
            raise CeleryTaskError(detail=str(e))

    def check_code(self):
        code = self.request.data.get("code")
        email = self.request.data.get("email")

        if code == RedisUtils.get_code_in_redis_from_email(email):
            RedisUtils.set_code_in_redis_from_email(email, code)
            return code

        raise CodeNotMatchError()
