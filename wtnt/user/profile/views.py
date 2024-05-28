from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from team.serializers import TeamListSerializer, TeamManageActivitySerializer
from team.models import TeamApply, Team, TeamUser, Likes
from team.utils import createSerializerHelper

from core.exceptions import IsNotOwner
from core.permissions import IsApprovedUser
from .service import ProfileService

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
        user_id = kwargs.get("user_id")
        keyword = request.query_params.get("keyword")
        if keyword == "apply":
            team_ids = TeamApply.objects.filter(user_id=user_id, is_approved=False).values_list("team_id", flat=True)
            team_data = Team.objects.filter(id__in=team_ids)
        else:
            team_ids = TeamUser.objects.filter(user_id=user_id).values_list("team_id", flat=True)
            if keyword == "accomplished":
                team_data = Team.objects.filter(id__in=team_ids, is_accomplished=True, is_approved=True)
            elif keyword == "inprogress":
                team_data = Team.objects.filter(id__in=team_ids, is_accomplished=False, is_approved=True)
            else:
                return Response({"error": "Wrong Keyword"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TeamListSerializer(team_data, many=True)
        data = createSerializerHelper.make_responses(serializer.data, request.user.id)
        is_owner = True if user_id == request.user.id else False

        return Response({"team": data, "is_owner": is_owner}, status=status.HTTP_200_OK)


class UserManageActivityView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, request, *args, **kwargs):
        owner_id = kwargs.get("user_id")
        if owner_id != request.user.id:
            raise IsNotOwner()

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
            raise IsNotOwner()

        like_team_ids = Likes.objects.filter(user_id=owner_id).values_list("team_id", flat=True)
        team_data = Team.objects.filter(id__in=like_team_ids)
        serializer = TeamListSerializer(team_data, many=True)
        data = createSerializerHelper.make_responses(serializer.data, owner_id)

        return Response({"team": data}, status=status.HTTP_200_OK)
