import core.exception.notfound as notfound_exception
import core.exception.team as team_exception
from core.service import BaseService
from core.utils.team import LikeResponse
from team.models import Likes, Team
from team.serializers import TeamLikeSerializer


class LikeService(BaseService):
    def like(self):
        user_id = self.request.user.id
        team_id = self.kwargs.get("team_id")
        version = self.request.data.get("version")

        try:
            team = Team.objects.get(id=team_id)
            like = Likes.objects.get(team_id=team_id, user_id=user_id)
            if version == team.version:
                like.delete()
                team.like -= 1
                team.version += 1
                team.save()

                return LikeResponse.make_data(team.like, False, team.version)

            raise team_exception.TeamLikeVersionError(current_version=team.version)

        except Team.DoesNotExist:
            raise notfound_exception.TeamNotFoundError()

        except Likes.DoesNotExist:
            if version == team.version:
                serializer = TeamLikeSerializer(data={"team_id": team_id, "user_id": user_id})
                if serializer.is_valid():
                    serializer.save()
                    team.like += 1
                    team.version += 1
                    team.save()

                    return LikeResponse.make_data(team.like, True, team.version)

            raise team_exception.TeamLikeVersionError(current_version=team.version)
