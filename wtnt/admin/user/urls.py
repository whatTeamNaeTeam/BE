from django.urls import path
from .views import (
    UserManageView,
    UserDeleteView,
    UserSearchView,
)

urlpatterns = [
    path("manage", UserManageView.as_view(), name="admin-user-manage"),
    path("list", UserDeleteView.as_view(), name="admin-user-list"),
    path("search", UserSearchView.as_view(), name="admin-user-search"),
]
