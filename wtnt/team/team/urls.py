from django.urls import path
from .views import TeamView, TeamApplyView, TeamDetailView

urlpatterns = [
    path("create", TeamView.as_view()),
    path("apply/<int:team_id>", TeamApplyView.as_view()),
    path("detail/<int:team_id>", TeamDetailView.as_view()),
]
