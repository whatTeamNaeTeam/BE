from django.urls import path, include

urlpatterns = [
    path("admin/team/", include("admin.team.urls")),
    path("admin/user/", include("admin.user.urls")),
]
