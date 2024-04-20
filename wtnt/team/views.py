from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from core.permissions import IsApprovedUser
from .serializers import TeamCreateSerializer
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

        return Response(createSerializer.data, status=status.HTTP_201_CREATED)
