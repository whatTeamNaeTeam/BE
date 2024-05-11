from django.urls import path
from .views import (
    UserManageView,
    UserDeleteView,
)

urlpatterns = [
    path("manage", UserManageView.as_view()),
    path("list", UserDeleteView.as_view()),
]
