from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from user.serializers import UserProfileSerializer, UserTechSerializer, UserUrlSerializer
from team.serializers import TeamListSerializer
from user.models import UserTech, UserUrls
from team.models import TeamApply, Team, TeamUser
from user.utils import profileSerializerHelper
from team.utils import createSerializerHelper
from core.exceptions import IsNotOwner

User = get_user_model()


class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            owner_id = request.user.id
        else:
            owner_id = 0
        user_id = kwargs.get("user_id")

        user_queryset = User.objects.get(id=user_id)
        if user_queryset:
            try:
                url_queryset = UserUrls.objects.get(user_id=user_id)
                url_serializer = url_serializer = UserUrlSerializer(url_queryset)
            except UserUrls.DoesNotExist:
                url_serializer = None
            try:
                tech_queryset = UserTech.objects.get(user_id=user_id)
                tech_serializer = UserTechSerializer(tech_queryset)
            except UserTech.DoesNotExist:
                tech_serializer = None

            user_serializer = UserProfileSerializer(user_queryset)

            return Response(
                profileSerializerHelper.make_data(owner_id, user_serializer, url_serializer, tech_serializer),
                status=status.HTTP_200_OK,
            )

        return Response({"error": "No Content"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            owner_id = request.user.id
        else:
            owner_id = 0
        user_id = kwargs.get("user_id")

        if user_id != owner_id:
            raise IsNotOwner()

        user = User.objects.get(id=user_id)
        explain = request.data.get("explain")
        serializer = UserProfileSerializer(user, data={"explain": explain}, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response({"explain": explain}, status=status.HTTP_202_ACCEPTED)

        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            owner_id = request.user.id
        else:
            owner_id = 0
        user_id = kwargs.get("user_id")

        if user_id != owner_id:
            raise IsNotOwner()

        user = User.objects.get(id=user_id)
        position = request.data.get("position")
        serializer = UserProfileSerializer(user, data={"position": position}, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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
