from django.urls import path
from .views import TeamView, TeamListView, TeamDetailView, LeaderCheckView

urlpatterns = [
    path("create", TeamView.as_view(), name="create-team"),
    path("list", TeamListView.as_view(), name="pagenated-team-main"),
    path("detail/<int:team_id>", TeamDetailView.as_view(), name="detail-team"),
    path("check-leader/<int:team_id>", LeaderCheckView.as_view(), name="leader-check"),
]
