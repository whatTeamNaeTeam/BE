from django.urls import path
from .views import (
    UserManageGetListView,
    UserManageUpdateView,
    UserDeleteView,
    UserGetListView,
    TeamManageGetListView,
    TeamManageUpdateView,
    TeamDeleteView,
    TeamDeleteGetListView,
)

urlpatterns = [
    path("admin/user/manage", UserManageGetListView.as_view()),
    path("admin/user/manage/<int:user_id>", UserManageUpdateView.as_view()),
    path("admin/user/list", UserGetListView.as_view()),
    path("admin/user/list/<int:user_id>", UserDeleteView.as_view()),
    path("admin/team/manage", TeamManageGetListView.as_view()),
    path("admin/team/manage/<int:team_id>", TeamManageUpdateView.as_view()),
    path("admin/team/delete", TeamDeleteGetListView.as_view()),
    path("admin/team/delete/<int:team_id>", TeamDeleteView.as_view()),
]
