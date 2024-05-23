from django.urls import path
from .views import (
    UserProfileView,
    UserTechView,
    UserUrlView,
    UserMyActivityView,
    UserManageActivityView,
    UserLikeTeamView,
)

urlpatterns = [
    path("<int:user_id>", UserProfileView.as_view()),
    path("tech/<int:user_id>", UserTechView.as_view()),
    path("url/<int:user_id>", UserUrlView.as_view()),
    path("activity/<int:user_id>", UserMyActivityView.as_view()),
    path("team-manage/<int:user_id>", UserManageActivityView.as_view()),
    path("like/<int:user_id>", UserLikeTeamView.as_view()),
]
