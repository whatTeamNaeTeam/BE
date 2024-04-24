from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from core.permissions import IsApprovedUser
from .serializers import TeamCreateSerializer, TeamUrlCreateSerializer, TeamTechCreateSerializer
from .utils import createSerializerHelper

# Create your views here.

User = get_user_model()


class CreateTeamView(APIView):
    permission_classes = [IsApprovedUser]

    def post(self, request, *args, **kwargs):
        url = createSerializerHelper.upload_s3(request.data.get("name"), request.FILES.get("image"))
        team_data = createSerializerHelper.make_data(request.user.id, request.data, url)
        createSerializer = TeamCreateSerializer(data=team_data)

        if createSerializer.is_valid():
            createSerializer.save()

            team_id = createSerializer.data.get("id")
            team_urls = createSerializerHelper.make_urls_data(team_id, request.data.getlist("urls"))
            urlSerializer = TeamUrlCreateSerializer(data=team_urls, many=True)

            if urlSerializer.is_valid():
                team_techs = createSerializerHelper.make_techs_data(
                    team_id, request.data.getlist("subCategory"), request.data.getlist("memberCount")
                )
                techSerializer = TeamTechCreateSerializer(data=team_techs, many=True)

                if techSerializer.is_valid():
                    techSerializer.save()
                    urlSerializer.save()

                    response = createSerializerHelper.make_response(
                        createSerializer.data, urlSerializer.data, techSerializer.data
                    )

                    return Response(response, status=status.HTTP_201_CREATED)

        return Response({"message": "Error"}, status=status.HTTP_400_BAD_REQUEST)
