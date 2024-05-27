from django.contrib.auth import get_user_model
from .utils import set_refresh_token_in_cache, get_user_info

User = get_user_model()


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
