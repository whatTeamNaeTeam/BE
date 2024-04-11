from django.urls import path
from .views import UserManageView

urlpatterns = [
    path("manage", UserManageView.as_view()),
]
