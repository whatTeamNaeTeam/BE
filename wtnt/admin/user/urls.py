from django.urls import path
from .views import (
    UserManageGetListView,
    UserManageUpdateView,
    UserDeleteView,
    UserGetListView,
)

urlpatterns = [
    path("manage", UserManageGetListView.as_view()),
    path("manage/<int:user_id>", UserManageUpdateView.as_view()),
    path("list", UserGetListView.as_view()),
    path("list/<int:user_id>", UserDeleteView.as_view()),
]
