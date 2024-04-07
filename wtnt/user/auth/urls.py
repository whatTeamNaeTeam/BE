from django.urls import path
from .views import GithubLoginView, GithubOAuthCallBackView, FinishGithubLoginView, WtntTokenRefreshView

urlpatterns = [
    path("github/callback", GithubOAuthCallBackView.as_view()),
    path("github/login", GithubLoginView.as_view()),
    path("github/finish", FinishGithubLoginView.as_view()),
    path("token/refresh", WtntTokenRefreshView.as_view()),
]
