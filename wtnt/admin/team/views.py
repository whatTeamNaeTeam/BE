from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model

from core.pagenations import ListPagenationSize10
from team.models import Team
from admin.serializers import ApproveTeamSerializer

User = get_user_model()


class TeamManageView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = ApproveTeamSerializer

    def get(self, request):
        queryset = Team.objects.filter(is_approved=False)
        serialzer = self.serializer_class(queryset, many=True)

        return Response(serialzer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        team_id = [int(id) for id in request.data.get("ids").split(",")]
        team = Team.objects.filter(id__in=team_id)
        team.update(is_approved=True)
        return Response({"success": True}, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, *args, **kwargs):
        team_id = [int(id) for id in request.data.get("ids").split(",")]
        try:
            team = Team.objects.filter(id__in=team_id)
            team.delete()

            return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)

        except User.DoesNotExist:
            return Response({"error": "Team Not Found"}, status=status.HTTP_404_NOT_FOUND)


class TeamDeleteView(APIView, ListPagenationSize10):
    permission_classes = [IsAdminUser]
    serializer_class = ApproveTeamSerializer

    def get(self, request):
        queryset = Team.objects.filter(is_approved=True).order_by("id")
        paginated = self.paginate_queryset(queryset, request, view=self)
        serializer = self.serializer_class(paginated, many=True)

        return self.get_paginated_response(serializer.data)

    def delete(self, request, *args, **kwargs):
        team_id = [int(id) for id in request.data.get("ids").split(",")]
        try:
            team = Team.objects.filter(id__in=team_id)
            team.delete()

            return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)

        except User.DoesNotExist:
            return Response({"error": "Team Not Found"}, status=status.HTTP_404_NOT_FOUND)
