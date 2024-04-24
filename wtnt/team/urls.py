from django.urls import path
from .views import CreateTeamView

urlpatterns = [
    path("team/create", CreateTeamView.as_view()),
]
