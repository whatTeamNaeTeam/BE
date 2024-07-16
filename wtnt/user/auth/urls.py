from django.urls import path
from .views import (
    GithubLoginView,
    LogoutView,
    GithubOAuthCallBackView,
    FinishGithubLoginView,
    WtntTokenRefreshView,
    EmailVerifyView,
)

urlpatterns = [
    path("github/callback", GithubOAuthCallBackView.as_view()),
    path("github/login", GithubLoginView.as_view(), name="github-login"),
    path("github/finish", FinishGithubLoginView.as_view(), name="github-finish"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("token/refresh", WtntTokenRefreshView.as_view(), name="token-refresh"),
    path("email", EmailVerifyView.as_view(), name="verify-email"),
]
