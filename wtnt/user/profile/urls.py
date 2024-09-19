from django.urls import path
from .views import (
    UserProfileView,
    UserTechView,
    UserUrlView,
    UserMyActivityView,
    UserManageActivityView,
    UserManageActivityDetailView,
    UserLikeTeamView,
    NotApprovedTeamView,
    UserProfileSecretView,
    UserProfileOwnerCheckView,
)

urlpatterns = [
    path("<int:user_id>", UserProfileView.as_view(), name="user-profile"),
    path("tech/<int:user_id>", UserTechView.as_view(), name="update-user-tech"),
    path("url/<int:user_id>", UserUrlView.as_view(), name="update-user-url"),
    path("activity/<int:user_id>", UserMyActivityView.as_view(), name="user-my-activity"),
    path("team-manage/<int:user_id>", UserManageActivityView.as_view(), name="profile-team-manage"),
    path("like/<int:user_id>", UserLikeTeamView.as_view(), name="like-team-list"),
    path("team-manage/detail/<int:team_id>", UserManageActivityDetailView.as_view(), name="profile-team-manage-detail"),
    path("<int:user_id>/not-approved", NotApprovedTeamView.as_view(), name="not-approved-team"),
    path("", UserProfileSecretView.as_view(), name="user-profile-secret"),
    path("check-owner/<int:user_id>", UserProfileOwnerCheckView.as_view(), name="profile-check-owner"),
]
