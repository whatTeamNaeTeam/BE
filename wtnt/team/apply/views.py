from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from team.utils import applySerializerHelper
from team.serializers import TeamApplySerializer
from team.models import TeamApply, Team, TeamTech, TeamUser
from core.exceptions import IsNotLeaderError
from core.permissions import IsApprovedUser


class TeamApplyView(APIView):
    permission_classes = [IsApprovedUser]
    serializer_class = TeamApplySerializer

    def get(self, request, *args, **kwargs):
        team_id = kwargs.get("team_id")
        queryset = TeamApply.objects.filter(is_approved=False, team_id=team_id)
        team = Team.objects.get(id=team_id)

        if team.leader != request.user.id:
            raise IsNotLeaderError()

        if queryset:
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No Content"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        bio = request.data.get("bio", None)
        tech = request.data.get("subCategory")
        user_id = request.user.id
        team_id = kwargs.get("team_id")

        teamTech = TeamTech.objects.get(team_id=team_id, tech=tech)
        if teamTech.need_num <= teamTech.current_num:
            return Response({"error": "마감된 분야입니다."}, status=status.HTTP_400_BAD_REQUEST)

        apply_data = applySerializerHelper.make_data(user_id, team_id, bio, tech)
        serializer = self.serializer_class(data=apply_data)

        if serializer.is_valid():
            try:
                serializer.save()
            except Exception:
                return Response({"error": "중복된 지원입니다"}, status=status.HTTP_406_NOT_ACCEPTABLE)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        id = kwargs.get("team_id")
        apply = TeamApply.objects.get(id=id)

        team = Team.objects.get(id=apply.team_id)
        team_tech = TeamTech.objects.get(team_id=team.id, tech=apply.tech)

        if team.leader != request.user.id:
            raise IsNotLeaderError()

        serializer = self.serializer_class(apply, data={"is_approved": True}, partial=True)
        if serializer.is_valid() and team_tech.current_num < team_tech.need_num:
            serializer.save()
            team_tech.current_num += 1
            team_tech.save()

            teamUser = TeamUser(team_id=team.id, user_id=request.user.id)
            teamUser.save()

            return Response({"success": True}, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        id = kwargs.get("team_id")
        try:
            apply = TeamApply.objects.get(id=id)

            team = Team.objects.get(id=apply.team_id)

            if team.leader != request.user.id:
                raise IsNotLeaderError()

            apply.delete()

            return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)

        except TeamApply.DoesNotExist:
            return Response({"error": "Apply Not Found"}, status=status.HTTP_404_NOT_FOUND)
