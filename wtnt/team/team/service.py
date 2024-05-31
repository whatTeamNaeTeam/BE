from core.exceptions import SerializerNotValidError, NotFoundError, IsNotLeaderError
from core.service import BaseService
from core.utils.team import S3Utils, RedisTeamUtils, TeamResponse
from team.models import TeamUser, Team
from team.serializers import TeamCreateSerializer


class TeamService(BaseService):
    def create_team(self):
        user_id = self.request.user.id
        url = S3Utils.upload_s3(self.request.data.get("name"), self.request.FILES.get("image"))
        team_data = TeamResponse.make_data(
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

    def update_team(self):
        user_id = self.request.user.id
        team_id = self.kwargs.get("team_id")

        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise NotFoundError()
        self.check_leader(user_id, team.leader.id)

        if self.request.FILES.get("image"):
            url = S3Utils.upload_s3(self.request.data.get("name"), self.request.FILES.get("image"))
        else:
            url = team.image

        team_data = TeamResponse.make_data(
            user_id,
            self.request.data,
            url,
            self.request.data.getlist("subCategory"),
            self.request.data.getlist("memberCount"),
        )
        serializer = TeamCreateSerializer(team, data=team_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return serializer.data

        raise SerializerNotValidError(detail=SerializerNotValidError.get_detail(serializer.errors))

    def check_leader(self, user_id, leader_id):
        if not (user_id == leader_id):
            raise IsNotLeaderError()

    def get_team_detail(self):
        team_id = self.kwargs.get("team_id")
        user_id = self.request.user.id if self.request.user.id else None

        try:
            team = Team.objects.get(id=team_id)
            redis_ans = RedisTeamUtils.sadd_view_client(team_id, user_id, self.request.META.get("REMOTE_ADDR"))
            if redis_ans:
                team.view += 1
                team.save()
            serializer = TeamCreateSerializer(team)

            return TeamResponse.get_detail_response(serializer.data, user_id)

        except Team.DoesNotExist:
            raise NotFoundError()
