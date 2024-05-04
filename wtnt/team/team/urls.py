from django.urls import path
from .views import TeamView, InProgressTeamView, TeamDetailView, AccomplishedTeamView

urlpatterns = [
    path("create", TeamView.as_view()),
    path("inprogress", InProgressTeamView.as_view()),
    path("accomplished", AccomplishedTeamView.as_view()),
    path("detail/<int:team_id>", TeamDetailView.as_view()),
]
