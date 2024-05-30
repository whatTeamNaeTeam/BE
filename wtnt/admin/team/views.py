from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model

from .service import AdminTeamService

User = get_user_model()


class TeamManageView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        admin_service = AdminTeamService(request)
        data = admin_service.get_not_approved_team()

        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        admin_service = AdminTeamService(request)
        data = admin_service.approve_teams()

        return Response(data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, *args, **kwargs):
        admin_service = AdminTeamService(request)
        data = admin_service.reject_teams(status=False)

        return Response(data, status=status.HTTP_204_NO_CONTENT)


class TeamDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        admin_service = AdminTeamService(request)
        return admin_service.get_approved_teams()

    def delete(self, request, *args, **kwargs):
        admin_service = AdminTeamService(request)
        data = admin_service.reject_teams(status=True)

        return Response(data, status=status.HTTP_204_NO_CONTENT)


class TeamSearchView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        admin_service = AdminTeamService(request)
        return admin_service.serach_teams()
