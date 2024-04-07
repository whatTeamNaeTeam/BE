from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth import get_user_model

import requests
import json

# Create your views here.

User = get_user_model()


class GithubLoginView(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = "http://localhost:8000/api/auth/github/callback"
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response_data = response.data

        if response_data["user"]["email"]:
            response_data["registered"] = True
        else:
            response_data["registered"] = False

        return Response(response_data, status=status.HTTP_200_OK)


class GithubOAuthCallBackView(APIView):
    def get(self, request: Request):
        if code := request.GET.get("code"):
            response = self.send_code_to_github_login_view(code)
            if response.status_code == 200:
                return Response(response.json(), status=status.HTTP_200_OK)
            return Response(
                {"error": "Failed to process with GithubLoginView"},
                status=response.status_code,
            )

    def send_code_to_github_login_view(self, code: str):
        url = "http://localhost:8000/api/auth/github/login"
        payload = {"code": code}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)

        return response


class FinishGithubLoginView(APIView):
    def post(self, request):
        request_data = json.loads(request.body)

        user_id = request_data["user_id"]
        extra_data = SocialAccount.objects.get(user_id=user_id).extra_data

        user = User.objects.get(id=user_id)
        user.student_num = str(request_data.get("student_num"))
        user.name = request_data.get("name")
        user.email = extra_data.get("login") + "@github.com"
        user.image = extra_data.get("avatar_url")

        user.save()

        return Response({"success": True}, status=status.HTTP_201_CREATED)


class WtntTokenRefreshView(TokenRefreshView):
    def post(self, request: Request, *args, **kwargs):
        refresh_token = request.META.get("HTTP_REFRESH", None)
        serializer = self.get_serializer(data={"refresh": refresh_token})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        token = serializer.validated_data
        response = Response({"success": True}, status=status.HTTP_200_OK)
        response["refresh"] = token["refresh"]
        response["access"] = token["access"]

        return response
