from django.urls import path
from .views import (
    TeamManageGetListView,
    TeamManageUpdateView,
    TeamDeleteView,
    TeamGetListView,
)

urlpatterns = [
    path("manage", TeamManageGetListView.as_view()),
    path("manage/<int:team_id>", TeamManageUpdateView.as_view()),
    path("list", TeamGetListView.as_view()),
    path("list/<int:team_id>", TeamDeleteView.as_view()),
]
