from django.urls import path, include

urlpatterns = [
    path("team/", include("team.team.urls")),
]
