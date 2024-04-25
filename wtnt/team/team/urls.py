from django.urls import path
from .views import TeamView, TeamApplyView

urlpatterns = [
    path("create", TeamView.as_view()),
    path("apply/<int:team_id>", TeamApplyView.as_view()),
]
