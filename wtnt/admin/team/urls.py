from django.urls import path
from .views import (
    TeamManageView,
    TeamDeleteView,
)

urlpatterns = [
    path("manage", TeamManageView.as_view()),
    path("list", TeamDeleteView.as_view()),
]
