from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django_redis import get_redis_connection

from datetime import timedelta, datetime

import requests
from user.serializers import UserSerializer
from user.tasks import send_email

# Create your views here.

client = get_redis_connection()
User = get_user_model()


class GithubLoginView(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        is_web = request.META.get("HTTP_X_FROM", None)
        if is_web == "web":
            self.callback_url = "https://local.whatmeow.shop:3001/oauth/callback/github"
        elif is_web == "app":
            self.callback_url = "myapp://auth"
        else:
            self.callback_url = "http://localhost:8000/api/auth/github/callback"

        response = super().post(request, *args, **kwargs)
        response_data = response.data
        refresh_token = response_data.get("refresh", None)
        access_token = response_data.get("access", None)
        user_id = response_data["user"]["pk"]

        if refresh_token:
            cache.set(user_id, refresh_token)
            cache.expire_at(user_id, datetime.now() + timedelta(days=7))
            response_data.pop("refresh")

        _, email = response_data["user"]["email"].split("@")
        response_data.pop("user")

        if "sample.com" in email:
            response_data["registered"] = False
        else:
            response_data["registered"] = True
            user = User.objects.get(id=user_id)
            response_data["user"] = {
                "name": user.name,
                "student_num": user.student_num,
                "id": user.id,
                "image": user.image,
            }

        response_data.pop("access")

        response = Response(response_data, status=status.HTTP_200_OK)
        response.headers["access"] = access_token

        return response


class GithubOAuthCallBackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request: Request):
        if code := request.GET.get("code"):
            # response = self.send_code_to_github_login_view(code)
            # if response.status_code == 200:
            return Response(code, status=status.HTTP_200_OK)
        # return Response(
        # {"error": "Failed to process with GithubLoginView"},
        # status=response.status_code,
        # )

    def send_code_to_github_login_view(self, code: str):
        url = "http://localhost:8000/api/auth/github/login"
        payload = {"code": code, "callback_url": "http://localhost:8000/api/auth/github/callback"}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)

        return response


class FinishGithubLoginView(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        code = request.data.get("code")
        email = request.data.get("email")
        if code != client.get(email):
            return Response({"error": "Code Not Matched"}, status=status.HTTP_400_BAD_REQUEST)

        extra_data = SocialAccount.objects.get(user_id=request.user.id).extra_data

        user = User.objects.get(id=request.user.id)
        user.student_num = str(request.data.get("student_num"))
        user.name = request.data.get("name")
        user.social_id = extra_data.get("id")
        user.email = extra_data.get("login") + "@github.com"
        user.image = extra_data.get("avatar_url")
        user.position = request.data.get("position")

        user.save()

        serializer = self.serializer_class(user)
        client.delete(email)
        return Response({"user": serializer.data}, status=status.HTTP_201_CREATED)


class WtntTokenRefreshView(TokenRefreshView):
    def post(self, request: Request, *args, **kwargs):
        _, access_token = request.META.get("HTTP_AUTHORIZATION").split(" ")
        user_id = AccessToken(access_token, verify=False).payload.get("user_id")

        refresh_token = cache.get(user_id)
        if not refresh_token:
            return Response({"error": "Expired Refresh Token"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        token = serializer.validated_data
        response = Response({"success": True}, status=status.HTTP_200_OK)

        response.headers["access"] = token["access"]

        return response


class EmailVerifyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.query_params.get("code")
        email = request.queyr_params.get("email")
        answer = client.get(email)
        if code == answer:
            client.set(email, code)
            return Response({"code": code}, status=status.HTTP_200_OK)
        else:
            return Response({"success": False}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        try:
            send_email.delay(email)
            return Response({"success": True}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
