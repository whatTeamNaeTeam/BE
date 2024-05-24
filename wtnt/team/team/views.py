from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection

from core.exceptions import IsNotLeaderException
from core.permissions import IsApprovedUser
from core.pagenations import TeamPagination
from team.serializers import TeamCreateSerializer, TeamListSerializer
from team.utils import createSerializerHelper
from team.models import Team, TeamUser

# Create your views here.
client = get_redis_connection("default")
User = get_user_model()


class TeamView(APIView):
    permission_classes = [IsApprovedUser]

    def post(self, request, *args, **kwargs):
        url = createSerializerHelper.upload_s3(request.data.get("name"), request.FILES.get("image"))
        team_data = createSerializerHelper.make_data(
            request.user.id, request.data, url, request.data.getlist("subCategory"), request.data.getlist("memberCount")
        )
        createSerializer = TeamCreateSerializer(data=team_data)

        if createSerializer.is_valid():
            team = createSerializer.save()
            #
            teamUser = TeamUser(team_id=team.id, user_id=request.user.id)
            teamUser.save()
            #
            return Response(createSerializer.data, status=status.HTTP_201_CREATED)

        return Response({"error": createSerializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class TeamDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        team_id = kwargs.get("team_id")

        if not request.user.id:
            user_id = 0
        else:
            user_id = request.user.id
        try:
            redis_ans = client.sadd(f"views:{team_id}", f"{user_id}_{request.META.get('REMOTE_ADDR')}")
            team = Team.objects.get(id=team_id)
            if redis_ans:
                team.view += 1
                team.save()
            teamSerializer = TeamCreateSerializer(team)
            response = createSerializerHelper.make_response(teamSerializer.data, request.user.id)

            return Response(response, status=status.HTTP_200_OK)

        except Team.DoesNotExist:
            return Response({"error": "No Content"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        team_id = kwargs.get("team_id")
        try:
            team = Team.objects.get(id=team_id)
            if team.leader != request.user.id:
                raise IsNotLeaderException()

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
            if team.leader != request.user.id:
                raise IsNotLeaderException()

            name = request.data.get("name")
            explain = request.data.get("explain")
            serializer = TeamCreateSerializer(team, data={"name": name, "explain": explain}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"name": name, "explain": explain}, status=status.HTTP_202_ACCEPTED)

        except Team.DoesNotExist:
            return Response({"error": "No Content"}, status=status.HTTP_404_NOT_FOUND)


class TeamListView(APIView, TeamPagination):
    permission_classes = [AllowAny]
    serializer_class = TeamListSerializer

    def get(self, request):
        keyword = request.query_params.get("keyword")
        if keyword == "inprogress":
            queryset = Team.objects.filter(is_accomplished=False).all()
        elif keyword == "accomplished":
            queryset = Team.objects.filter(is_accomplished=True).all()
        else:
            return Response({"error": "Keyword Not Matched"}, status=status.HTTP_400_BAD_REQUEST)

        if queryset:
            paginated = self.paginate_queryset(queryset, request, view=self)
            serializer = self.serializer_class(paginated, many=True)
            data = createSerializerHelper.make_responses(serializer.data, request.user.id)
            return self.get_paginated_response(data)
        else:
            return Response({"error": "No Content"}, status=status.HTTP_404_NOT_FOUND)
