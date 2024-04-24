from django.urls import path
from .views import UserManageView, UserDeleteView

urlpatterns = [
    path("admin/manage", UserManageView.as_view()),
    path("admin/manage/<int:user_id>", UserManageView.as_view()),
    path("admin/delete", UserDeleteView.as_view()),
    path("admin/delete/<int:user_id>", UserDeleteView.as_view()),
]
