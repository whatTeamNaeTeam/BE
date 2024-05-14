from django.urls import path, include

urlpatterns = [
    path("team/", include("team.team.urls")),
    path("apply/", include("team.apply.urls")),
    path("like/", include("team.like.urls")),
]
