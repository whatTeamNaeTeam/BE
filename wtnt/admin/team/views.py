from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model

from core.pagenations import ListPagenationSize10
from team.models import Team
from admin.serializers import ApproveTeamSerializer

User = get_user_model()


class TeamManageGetListView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = ApproveTeamSerializer

    def get(self, request):
        queryset = Team.objects.filter(is_approved=False)
        serialzer = self.serializer_class(queryset, many=True)

        return Response(serialzer.data, status=status.HTTP_200_OK)


class TeamManageUpdateView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = ApproveTeamSerializer

    def patch(self, request, *args, **kwargs):
        team_id = kwargs.get("team_id")
        team = Team.objects.get(id=team_id)

        serializer = self.serializer_class(team, data={"is_approved": True}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True}, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        team_id = kwargs.get("team_id")
        try:
            team = Team.objects.get(id=team_id)
            team.delete()

            return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)

        except User.DoesNotExist:
            return Response({"error": "Team Not Found"}, status=status.HTTP_404_NOT_FOUND)


class TeamGetListView(APIView, ListPagenationSize10):
    permission_classes = [IsAdminUser]
    serializer_class = ApproveTeamSerializer

    def get(self, request):
        queryset = Team.objects.filter(is_approved=True).order_by("id")
        paginated = self.paginate_queryset(queryset, request, view=self)
        serializer = self.serializer_class(paginated, many=True)

        return self.get_paginated_response(serializer.data)


class TeamDeleteView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = ApproveTeamSerializer

    def delete(self, request, *args, **kwargs):
        team_id = kwargs.get("team_id")
        try:
            team = Team.objects.get(id=team_id)
            team.delete()

            return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)

        except User.DoesNotExist:
            return Response({"error": "Team Not Found"}, status=status.HTTP_404_NOT_FOUND)
