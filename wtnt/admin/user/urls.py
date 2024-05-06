from django.urls import path
from .views import (
    UserManageGetListView,
    UserManageUpdateView,
    UserDeleteView,
    UserGetListView,
)

urlpatterns = [
    path("admin/user/manage", UserManageGetListView.as_view()),
    path("admin/user/manage/<int:user_id>", UserManageUpdateView.as_view()),
    path("admin/user/list", UserGetListView.as_view()),
    path("admin/user/list/<int:user_id>", UserDeleteView.as_view()),
]
