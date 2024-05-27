from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection

import requests
from .service import AuthService, RegisterService, RefreshService
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
        register_service = RegisterService(request)
        user = register_service.finish_register_by_user_input()
        serializer = self.serializer_class(user)

        return Response({"user": serializer.data}, status=status.HTTP_201_CREATED)


class WtntTokenRefreshView(TokenRefreshView):
    def post(self, request: Request, *args, **kwargs):
        refresh_service = RefreshService(request)
        refresh_token = refresh_service.extract_refresh_token()

        serializer = self.get_serializer(data={"refresh": refresh_token})
        token = refresh_service.get_new_access_token_from_serializer(serializer)

        response = Response({"detail": "Success to Token Refreshing"}, status=status.HTTP_200_OK)
        response.headers["access"] = token["access"]

        return response


class EmailVerifyView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, *args, **kwargs):
        code = request.data.get("code")
        email = request.data.get("email")
        answer = client.get(email).decode()
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
