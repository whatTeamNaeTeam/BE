from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection

from .utils import set_refresh_token_in_cache, get_user_info
from core.exceptions import CodeNotMatchError

User = get_user_model()
client = get_redis_connection()


class AuthService:
    def __init__(self, request):
        self.request = request

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
            set_refresh_token_in_cache(user_id, refresh_token)
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


class RegisterService:
    def __init__(self, request):
        self.request = request

    def finish_register_by_user_input(self):
        code = self.request.data.get("code")
        email = self.request.data.get("email")
        if code != client.get(email).decode():
            raise CodeNotMatchError()

        extra_data = SocialAccount.objects.get(user_id=self.request.user.id).extra_data
        user = User.objects.get(id=self.request.user.id)
        user.finish_register(extra_data=extra_data, request_data=self.request.data)

        client.delete(email)

        return user
