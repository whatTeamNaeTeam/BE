from django.urls import path, include

urlpatterns = [
    path("auth/", include("user.auth.urls")),
    path("profile/", include("user.profile.urls")),
]
