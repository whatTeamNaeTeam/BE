from django.urls import path
from .views import UserManageView, UserDeleteView

urlpatterns = [
    path("manage", UserManageView.as_view()),
    path("manage/<int:user_id>", UserManageView.as_view()),
    path("delete", UserDeleteView.as_view()),
    path("delete/<int:user_id>", UserDeleteView.as_view()),
]
