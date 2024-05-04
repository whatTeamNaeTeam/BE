from rest_framework import status
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model

from core.permissions import IsApprovedUser
from team.serializers import TeamCreateSerializer, TeamTechCreateSerializer, TeamListSerializer
from team.utils import createSerializerHelper
from team.models import Team, TeamTech

# Create your views here.

User = get_user_model()


class TeamView(APIView):
    permission_classes = [IsApprovedUser]

    def post(self, request, *args, **kwargs):
        url = createSerializerHelper.upload_s3(request.data.get("name"), request.FILES.get("image"))
        team_data = createSerializerHelper.make_data(request.user.id, request.data, url)
        createSerializer = TeamCreateSerializer(data=team_data)

        if createSerializer.is_valid():
            createSerializer.save()

            team_id = createSerializer.data.get("id")
            team_techs = createSerializerHelper.make_techs_data(
                team_id, request.data.getlist("subCategory"), request.data.getlist("memberCount")
            )
            techSerializer = TeamTechCreateSerializer(data=team_techs, many=True)

            if techSerializer.is_valid():
                techSerializer.save()
                response = createSerializerHelper.make_response(createSerializer.data, techSerializer.data)
                response["team"]["leader_name"] = request.user.name

                return Response(response, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": techSerializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": createSerializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class TeamDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        team_id = kwargs.get("team_id")
        try:
            team = Team.objects.get(id=team_id)
            teamSerializer = TeamCreateSerializer(team)

            team_tech = TeamTech.objects.filter(team_id=team_id)

            techSerializer = TeamTechCreateSerializer(team_tech, many=True)
            is_leader = True if request.user.id == team.leader.id else False

            response = createSerializerHelper.make_response(teamSerializer.data, techSerializer.data)
            response["team"]["leader_name"] = team.leader.name
            response["is_leader"] = is_leader

            return Response(response, status=status.HTTP_200_OK)

        except Team.DoesNotExist:
            return Response({"error": "No Content"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        team_id = kwargs.get("team_id")
        try:
            team = Team.objects.get(id=team_id)
            if team.leader.id != request.user.id:
                return Response({"error": "No Permission"}, status=status.HTTP_403_FORBIDDEN)

            url = request.data.get("urls")
            serializer = TeamCreateSerializer(team, {"url": url}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"urls": url.split(",")}, status=status.HTTP_202_ACCEPTED)

        except Team.DoesNotExist:
            return Response({"error": "No Content"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        team_id = kwargs.get("team_id")
        try:
            team = Team.objects.get(id=team_id)
            if team.leader.id != request.user.id:
                return Response({"error": "No Permission"}, status=status.HTTP_403_FORBIDDEN)

            name = request.data.get("name")
            explain = request.data.get("explain")
            serializer = TeamCreateSerializer(team, data={"name": name, "explain": explain}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"name": name, "explain": explain}, status=status.HTTP_202_ACCEPTED)

        except Team.DoesNotExist:
            return Response({"error": "No Content"}, status=status.HTTP_404_NOT_FOUND)


class TeamPagination(CursorPagination):
    page_size = 2
    ordering = "created_at"


class InProgressTeamView(APIView, TeamPagination):
    permission_classes = [AllowAny]
    serializer_class = TeamListSerializer

    def get(self, request):
        queryset = Team.objects.filter(is_accomplished=False).all()
        if queryset:
            paginated = self.paginate_queryset(queryset, request, view=self)
            serializer = self.serializer_class(paginated, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return Response({"error": "No Content"}, status=status.HTTP_404_NOT_FOUND)


class AccomplishedTeamView(APIView, TeamPagination):
    permission_classes = [AllowAny]
    serializer_class = TeamListSerializer

    def get(self, request):
        queryset = Team.objects.filter(is_accomplished=True).all()
        if queryset:
            paginated = self.paginate_queryset(queryset, request, view=self)
            serializer = self.serializer_class(paginated, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            return Response({"error": "No Content"}, status=status.HTTP_404_NOT_FOUND)
