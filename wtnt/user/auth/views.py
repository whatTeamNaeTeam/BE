from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection

import core.exception.request as exception
import requests
from .service import AuthService, RegisterService, RefreshService, EmailVerifyService
from user.serializers import UserSerializer

# Create your views here.

client = get_redis_connection()
User = get_user_model()


class GithubLoginView(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        required_field = ["code"]
        if len(request.data) != len(required_field):
            raise exception.InvalidRequestError()
        for field in required_field:
            if field not in request.data:
                raise exception.InvalidRequestError()

        auth_service = AuthService(request)
        self.callback_url = auth_service.determine_callback_url()

        response = super().post(request, *args, **kwargs)
        response_data, access_token = auth_service.process_response_data(response.data)

        response = Response(response_data, status=status.HTTP_200_OK)
        response.headers["access"] = access_token

        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        auth_service = AuthService(request)
        auth_service.logout()

        response = Response("", status=status.HTTP_204_NO_CONTENT)
        response.headers["access"] = ""

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
        required_field = ["student_num", "code", "email", "name", "position"]
        if len(request.data) != len(required_field):
            raise exception.InvalidRequestError()
        for field in required_field:
            if field not in request.data:
                raise exception.InvalidRequestError()

        register_service = RegisterService(request)
        data = register_service.finish_register_by_user_input()

        return Response({"user": data}, status=status.HTTP_201_CREATED)


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
        required_field = ["code", "email"]
        if len(request.data) != len(required_field):
            raise exception.InvalidRequestError()
        for field in required_field:
            if field not in request.data:
                raise exception.InvalidRequestError()

        email_verify_service = EmailVerifyService(request)
        code = email_verify_service.check_code()

        return Response({"code": code}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        required_field = ["email"]
        if len(request.data) != len(required_field):
            raise exception.InvalidRequestError()
        for field in required_field:
            if field not in request.data:
                raise exception.InvalidRequestError()

        email_verify_service = EmailVerifyService(request)
        email_verify_service.send_email()

        return Response({"detail": "Success to Send Email"}, status=status.HTTP_200_OK)
