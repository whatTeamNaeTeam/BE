from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsApprovedUser
from team.models import Team, Likes
from team.serializers import TeamLikeSerializer


class TeamLikeView(APIView):
    permission_classes = [IsApprovedUser]
    serializer_class = TeamLikeSerializer

    def post(self, request, *args, **kwargs):
        user_id = request.user.id
        team_id = kwargs.get("team_id")
        version = request.data.get("version")

        try:
            team = Team.objects.get(id=team_id)
            like = Likes.objects.get(team_id=team_id, user_id=user_id)
            if version == team.version:
                like.delete()
                team.like -= 1
                team.version += 1
                team.save()

                return Response(
                    {"like": {"like_count": team.like, "is_like": False}, "version": team.version},
                    status=status.HTTP_202_ACCEPTED,
                )
            return Response({"error": "Version Not Matched"}, status=status.HTTP_400_BAD_REQUEST)

        except Team.DoesNotExist:
            return Response({"errors": "Team Not Found"}, status=status.HTTP_404_NOT_FOUND)

        except Likes.DoesNotExist:
            if version == team.version:
                serializer = self.serializer_class(data={"team_id": team_id, "user_id": user_id})
                if serializer.is_valid():
                    serializer.save()
                    team.like += 1
                    team.version += 1
                    team.save()
                    return Response(
                        {"like": {"like_count": team.like, "is_like": True}, "version": team.version},
                        status=status.HTTP_202_ACCEPTED,
                    )
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "Version Not Matched"}, status=status.HTTP_400_BAD_REQUEST)
