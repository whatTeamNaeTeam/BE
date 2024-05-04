from django.urls import path
from .views import TeamApplyView

urlpatterns = [
    path("apply/<int:team_id>", TeamApplyView.as_view()),
]
