from django.urls import path
from .views import (
    TeamManageGetListView,
    TeamManageUpdateView,
    TeamDeleteView,
    TeamGetListView,
)

urlpatterns = [
    path("admin/team/manage", TeamManageGetListView.as_view()),
    path("admin/team/manage/<int:team_id>", TeamManageUpdateView.as_view()),
    path("admin/team/list", TeamGetListView.as_view()),
    path("admin/team/list/<int:team_id>", TeamDeleteView.as_view()),
]
