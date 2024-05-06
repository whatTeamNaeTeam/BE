from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model

from team.models import Team
from .serializers import ApproveUserSerializer, ApproveTeamSerializer

User = get_user_model()


class UserManageGetListView(APIView):
    serializer_class = ApproveUserSerializer
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = User.objects.filter(is_approved=False, is_superuser=False)
        if queryset:
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No Content"}, status=status.HTTP_404_NOT_FOUND)


class UserManageUpdateView(APIView):
    serializer_class = ApproveUserSerializer
    permission_classes = [IsAdminUser]

    def patch(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        user = User.objects.get(id=user_id)

        serializer = ApproveUserSerializer(user, data={"is_approved": True}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True}, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            user.delete()

            return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)

        except User.DoesNotExist:
            return Response({"error": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)


class UserListPagenation(PageNumberPagination):
    page_size = 10


class UserGetListView(APIView, UserListPagenation):
    permission_classes = [IsAdminUser]
    serializer_class = ApproveUserSerializer

    def get(self, request):
        queryset = User.objects.filter(is_approved=True, is_superuser=False).order_by("student_num")
        paginated = self.paginate_queryset(queryset, request, view=self)
        serializer = self.serializer_class(paginated, many=True)

        return self.get_paginated_response(serializer.data)


class UserDeleteView(APIView):
    serializer_class = ApproveUserSerializer
    permission_classes = [IsAdminUser]

    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            user.delete()

            return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)

        except User.DoesNotExist:
            return Response({"error": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)


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


class TeamDeleteGetListView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = ApproveTeamSerializer

    def get(self, request):
        queryset = Team.objects.filter(is_approved=True)
        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


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
