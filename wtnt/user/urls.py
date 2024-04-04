from django.urls import path
from .views import GithubLoginView, GithubOAuthCallBackView

urlpatterns = [
    path("github/callback", GithubOAuthCallBackView.as_view()),
    path("github/login", GithubLoginView.as_view()),
]