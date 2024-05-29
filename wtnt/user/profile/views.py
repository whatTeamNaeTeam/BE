from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from team.serializers import TeamListSerializer, TeamManageActivitySerializer
from team.models import Team, TeamUser, Likes
from team.utils import createSerializerHelper

from core.exceptions import IsNotOwnerError
from core.permissions import IsApprovedUser
from .service import ProfileService, MyActivityServcie

User = get_user_model()


class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        profile_service = ProfileService(request, **kwargs)
        data = profile_service.process_response_data()

        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        profile_service = ProfileService(request, **kwargs)
        profile_service.check_ownership()
        data = profile_service.update_user_info()

        return Response(data, status=status.HTTP_202_ACCEPTED)


class UserTechView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        profile_service = ProfileService(request, **kwargs)
        profile_service.check_ownership()
        data = profile_service.update_tech_info()

        return Response(data, status=status.HTTP_202_ACCEPTED)


class UserUrlView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        profile_service = ProfileService(request, **kwargs)
        profile_service.check_ownership()
        data = profile_service.update_user_url_info()

        return Response(data, status=status.HTTP_202_ACCEPTED)


class UserMyActivityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        myactivity_service = MyActivityServcie(request, **kwargs)
        data = myactivity_service.get_my_activity()

        return Response(data, status=status.HTTP_200_OK)


class UserManageActivityView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, request, *args, **kwargs):
        owner_id = kwargs.get("user_id")
        if owner_id != request.user.id:
            raise IsNotOwnerError()

        team_ids = TeamUser.objects.filter(user_id=owner_id).values_list("team_id", flat=True)
        team_data = Team.objects.filter(id__in=team_ids)
        serializer = TeamManageActivitySerializer(team_data, many=True)
        data = createSerializerHelper.make_responses(serializer.data, request.user.id, is_manage=True)

        return Response({"team": data}, status=status.HTTP_200_OK)


class UserLikeTeamView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, request, *args, **kwargs):
        owner_id = kwargs.get("user_id")
        if owner_id != request.user.id:
            raise IsNotOwnerError()

        like_team_ids = Likes.objects.filter(user_id=owner_id).values_list("team_id", flat=True)
        team_data = Team.objects.filter(id__in=like_team_ids)
        serializer = TeamListSerializer(team_data, many=True)
        data = createSerializerHelper.make_responses(serializer.data, owner_id)

        return Response({"team": data}, status=status.HTTP_200_OK)
