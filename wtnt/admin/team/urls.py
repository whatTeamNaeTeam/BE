from django.urls import path
from .views import (
    TeamManageView,
    TeamDeleteView,
    TeamSearchView,
)

urlpatterns = [
    path("manage", TeamManageView.as_view(), name="admin-team-manage"),
    path("list", TeamDeleteView.as_view(), name="admin-team-list"),
    path("search", TeamSearchView.as_view(), name="admin-team-search"),
]
