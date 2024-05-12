from django.urls import path
from .views import (
    TeamManageView,
    TeamDeleteView,
    TeamSearchView,
)

urlpatterns = [
    path("manage", TeamManageView.as_view()),
    path("list", TeamDeleteView.as_view()),
    path("search", TeamSearchView.as_view()),
]
