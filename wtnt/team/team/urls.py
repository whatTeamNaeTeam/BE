from django.urls import path
from .views import TeamView

urlpatterns = [
    path("create", TeamView.as_view()),
]
