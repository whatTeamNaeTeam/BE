from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from core.permissions import IsApprovedUser
from team.serializers import (
    TeamCreateSerializer,
    TeamUrlCreateSerializer,
    TeamTechCreateSerializer,
    TeamApplySerializer,
)
from team.utils import createSerializerHelper, applySerializerHelper

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
                if request.data.getlist("urls", None):
                    team_urls = createSerializerHelper.make_urls_data(team_id, request.data.getlist("urls"))
                    urlSerializer = TeamUrlCreateSerializer(data=team_urls, many=True)

                    if urlSerializer.is_valid():
                        techSerializer.save()
                        urlSerializer.save()

                        response = createSerializerHelper.make_full_response(
                            createSerializer.data, urlSerializer.data, techSerializer.data
                        )
                else:
                    response = createSerializerHelper.make_response(createSerializer.data, techSerializer.data)

                return Response(response, status=status.HTTP_201_CREATED)

        return Response({"message": "Error"}, status=status.HTTP_400_BAD_REQUEST)


class TeamApplyView(APIView):
    permission_classes = [IsApprovedUser]
    serializer_class = TeamApplySerializer

    def post(self, request, *args, **kwargs):
        bio = request.data.get("bio", None)
        user_id = request.user.id
        team_id = kwargs.get("team_id")

        apply_data = applySerializerHelper.make_data(user_id, team_id, bio)
        serializer = self.serializer_class(data=apply_data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
