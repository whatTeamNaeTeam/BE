from core.exceptions import SerializerNotValidError
from core.service import BaseService
from core.utils.team import S3Utils, make_data
from team.models import TeamUser
from team.serializers import TeamCreateSerializer


class TeamService(BaseService):
    def create_team(self):
        user_id = self.request.user.id
        url = S3Utils.upload_s3(self.request.data.get("name"), self.request.FILES.get("image"))
        team_data = make_data(
            user_id,
            self.request.data,
            url,
            self.request.data.getlist("subCategory"),
            self.request.data.getlist("memberCount"),
        )
        serializer = TeamCreateSerializer(data=team_data)

        if serializer.is_valid():
            team = serializer.save()

            teamUser = TeamUser(team_id=team.id, user_id=user_id)
            teamUser.save()

            return serializer.data

        raise SerializerNotValidError(detail=SerializerNotValidError.get_detail(serializer.errors))
