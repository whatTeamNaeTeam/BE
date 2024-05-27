from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from user.serializers import UserTechSerializer, UserUrlSerializer
from team.serializers import TeamListSerializer, TeamManageActivitySerializer
from user.models import UserTech, UserUrls
from team.models import TeamApply, Team, TeamUser, Likes
from user.utils import profileSerializerHelper
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
        explain, position = profile_service.update_user_info()

        return Response({"explain": explain, "position": position}, status=status.HTTP_202_ACCEPTED)


class UserTechView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserTechSerializer

    def post(self, request, *args, **kwargs):
        owner_id = kwargs.get("user_id")
        user_id = request.user.id
        tech = request.data.get("tech")

        if owner_id != user_id:
            raise IsNotOwner()

        user_tech = UserTech.objects.filter(user_id=user_id).first()

        if user_tech:
            serializer = self.serializer_class(user_tech, data={"tech": tech}, partial=True)

        else:
            data = {"user_id": owner_id, "tech": tech}
            serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({"tech": profileSerializerHelper.make_tech_data(tech)}, status=status.HTTP_202_ACCEPTED)

        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserUrlView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserUrlSerializer

    def post(self, request, *args, **kwargs):
        owner_id = kwargs.get("user_id")
        user_id = request.user.id
        url = request.data.get("url")

        if owner_id != user_id:
            raise IsNotOwner()

        user_url = UserUrls.objects.filter(user_id=user_id).first()

        if user_url:
            serializer = self.serializer_class(user_url, data={"url": url}, partial=True)
        else:
            data = {"user_id": owner_id, "url": url}
            serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({"urls": profileSerializerHelper.make_url_data(url)}, status=status.HTTP_202_ACCEPTED)

        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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
