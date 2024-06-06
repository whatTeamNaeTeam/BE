from django.urls import path
from .views import TeamView, TeamListView, TeamDetailView

urlpatterns = [
    path("create", TeamView.as_view(), name="create-team"),
    path("list", TeamListView.as_view(), name="pagenated-team-main"),
    path("detail/<int:team_id>", TeamDetailView.as_view(), name="detail-team"),
]
