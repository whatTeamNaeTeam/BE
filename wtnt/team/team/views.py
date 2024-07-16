from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection

import core.exception.request as exception
from core.permissions import IsApprovedUser
from .service import TeamService

# Create your views here.
client = get_redis_connection("default")
User = get_user_model()


class TeamView(APIView):
    permission_classes = [IsApprovedUser]

    def post(self, request, *args, **kwargs):
        required_field = ["title", "genre", "explain", "subCategory", "memberCount"]
        if 5 <= len(request.data) <= 7:
            raise exception.InvalidRequestError()
        for field in required_field:
            if field not in request.data:
                raise exception.InvalidRequestError()

        team_service = TeamService(request)
        data = team_service.create_team()
        return Response(data, status=status.HTTP_201_CREATED)


class TeamDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        team_service = TeamService(request, **kwargs)
        data = team_service.get_team_detail()

        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        required_field = ["title", "genre", "explain", "subCategory", "memberCount"]
        if 5 <= len(request.data) <= 7:
            raise exception.InvalidRequestError()
        for field in required_field:
            if field not in request.data:
                raise exception.InvalidRequestError()

        team_service = TeamService(request, **kwargs)
        data = team_service.update_team()

        return Response(data, status=status.HTTP_202_ACCEPTED)


class TeamListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        team_service = TeamService(request)
        return team_service.get_paginated_team_list()
