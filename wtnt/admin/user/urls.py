from django.urls import path
from .views import (
    UserManageView,
    UserDeleteView,
    UserSearchView,
)

urlpatterns = [
    path("manage", UserManageView.as_view()),
    path("list", UserDeleteView.as_view()),
    path("search", UserSearchView.as_view()),
]
