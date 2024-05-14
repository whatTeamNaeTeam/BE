from django.urls import path
from .views import TeamView, TeamListView, TeamDetailView

urlpatterns = [
    path("create", TeamView.as_view()),
    path("list", TeamListView.as_view()),
    path("detail/<int:team_id>", TeamDetailView.as_view()),
]
