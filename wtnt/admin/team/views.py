from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from django.db.models import Q

from core.pagenations import ListPagenationSize10
from team.models import Team
from admin.serializers import ApproveTeamSerializer
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


class TeamSearchView(APIView, ListPagenationSize10):
    permission_classes = [IsAdminUser]
    serializer_class = ApproveTeamSerializer

    def get(self, request):
        keyword = request.query_params.get("keyword")
        search_filter = request.query_params.get("filter")

        try:
            if search_filter == "name":
                queryset = Team.objects.filter(Q(name__icontains=keyword), is_approved=True).order_by("id")
            elif search_filter == "genre":
                queryset = Team.objects.filter(Q(genre__icontains=keyword), is_approved=True).order_by("id")
            elif search_filter == "leader":
                leader = User.objects.get(name=keyword)
                queryset = Team.objects.filter(leader_id=leader.id, is_approved=True).order_by("id")
            else:
                return Response({"error": "No Filter"}, status=status.HTTP_400_BAD_REQUEST)

            paginated = self.paginate_queryset(queryset, request, view=self)
            serializer = self.serializer_class(paginated, many=True)

            return self.get_paginated_response(serializer.data)

        except Team.DoesNotExist:
            return Response({"error": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)
