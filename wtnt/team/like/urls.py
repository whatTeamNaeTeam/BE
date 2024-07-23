from django.urls import path
from .views import TeamLikeView

urlpatterns = [
    path("<int:team_id>", TeamLikeView.as_view(), name="like-team"),
]
