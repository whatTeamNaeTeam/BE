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

import requests
from .service import AuthService
from user.serializers import UserSerializer
from user.tasks import send_email

# Create your views here.

client = get_redis_connection()
User = get_user_model()


class GithubLoginView(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        auth_service = AuthService(request)
        self.callback_url = auth_service.determine_callback_url()

        response = super().post(request, *args, **kwargs)
        response_data, access_token = auth_service.process_response_data(response.data)

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

    def patch(self, request, *args, **kwargs):
        code = request.data.get("code")
        email = request.data.get("email")
        answer = client.get(email)
        if code == answer:
            client.set(email, code)
            return Response({"code": code}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Code not Matched"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        try:
            send_email.delay(email)
            return Response({"detail": "Succes to send Email"}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)
