from django.urls import path
from .views import UserProfileView, UserTechView, UserUrlView

urlpatterns = [
    path("<int:user_id>", UserProfileView.as_view()),
    path("tech/<int:user_id>", UserTechView.as_view()),
    path("url/<int:user_id>", UserUrlView.as_view()),
]
