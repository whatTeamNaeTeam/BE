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
from team.models import TeamApply, Team

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

    def get(self, request, *args, **kwargs):
        team_id = kwargs.get("team_id")
        queryset = TeamApply.objects.filter(is_approved=False, team_id=team_id)
        team = Team.objects.get(id=team_id)

        if team.leader != request.user.id:
            return Response({"error": "No Permission"}, status=status.HTTP_403_FORBIDDEN)

        if queryset:
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No Content"}, status=status.HTTP_404_NOT_FOUND)

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

    def patch(self, request, *args, **kwargs):
        id = kwargs.get("team_id")
        apply = TeamApply.objects.get(id=id)

        team = Team.objects.get(id=apply.team_id)

        if team.leader != request.user.id:
            return Response({"error": "No Permission"}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(apply, data={"is_approved": True}, partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response({"success": True}, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        id = kwargs.get("team_id")
        try:
            apply = TeamApply.objects.get(id=id)

            team = Team.objects.get(id=apply.team_id)

            if team.leader != request.user.id:
                return Response({"error": "No Permission"}, status=status.HTTP_403_FORBIDDEN)

            apply.delete()

            return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)

        except TeamApply.DoesNotExist:
            return Response({"error": "Apply Not Found"}, status=status.HTTP_404_NOT_FOUND)
