from django.core.cache import cache

import core.exception.team as team_exception
import core.exception.notfound as notfound_exception
from core.pagenations import TeamPagination
from core.service import BaseServiceWithCheckLeader
from core.utils.team import TeamResponse
from core.utils.redis import RedisUtils
from core.utils.s3 import S3Utils
from team.models import TeamUser, Team
from team.serializers import TeamCreateSerializer, TeamListSerializer


class TeamService(BaseServiceWithCheckLeader, TeamPagination):
    def create_team(self):
        user_id = self.request.user.id
        url, uuid = S3Utils.upload_team_image_on_s3(self.request.FILES.get("image", None))

        team_data = TeamResponse.make_data(
            user_id,
            self.request.data,
            url,
            self.request.data.getlist("subCategory"),
            self.request.data.getlist("memberCount"),
            uuid,
        )
        serializer = TeamCreateSerializer(data=team_data)

        if serializer.is_valid():
            team = serializer.save()

            teamUser = TeamUser(team_id=team.id, user_id=user_id, tech="팀장")
            teamUser.save()

            return TeamResponse.get_detail_response(serializer.data, user_id)

    def update_team(self):
        user_id = self.request.user.id
        team_id = self.kwargs.get("team_id")

        try:
            team = Team.objects.prefetch_related("category").get(id=team_id)
        except Team.DoesNotExist:
            raise notfound_exception.TeamNotFoundError()
        self.check_leader(user_id, team.leader.id)

        if self.request.FILES.get("image", None):
            url, _ = S3Utils.upload_team_image_on_s3(self.request.FILES.get("image"), id=team.uuid)
        else:
            url = team.image

        team_data = TeamResponse.make_data(
            user_id,
            self.request.data,
            url,
            self.request.data.getlist("subCategory"),
            self.request.data.getlist("memberCount"),
            team.uuid,
        )
        serializer = TeamCreateSerializer(team, data=team_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return TeamResponse.get_detail_response(serializer.data, user_id)

    def get_team_data_from_id(self, team_id):
        try:
            team = Team.objects.select_related("leader").prefetch_related("category").get(id=team_id)
            serializer = TeamCreateSerializer(team)
            return serializer.data
        except Team.DoesNotExist:
            raise notfound_exception.TeamNotFoundError()

    def get_team_detail(self):
        team_id = self.kwargs.get("team_id")
        user_id = self.request.user.id if self.request.user.id else None
        cache_key = f"team_detail_{team_id}"

        team = cache.get(cache_key)

        redis_ans = RedisUtils.sadd_view_client(team_id, user_id, self.request.META.get("REMOTE_ADDR"))

        if team is None:
            team = self.get_team_data_from_id(team_id)

        if redis_ans:
            team["view"] += 1
            RedisUtils.sadd_view_update_list(team_id)

        cache.set(cache_key, team, timeout=60 * 10)

        return TeamResponse.get_detail_response(team, user_id)

    def get_paginated_team_list(self):
        user_id = self.request.user.id
        keyword = self.request.query_params.get("keyword")

        if keyword == "inprogress":
            queryset = (
                Team.objects.filter(is_accomplished=False, is_approved=True)
                .select_related("leader")
                .prefetch_related("category")
                .all()
            )
        elif keyword == "accomplished":
            queryset = (
                Team.objects.filter(is_accomplished=True, is_approved=True)
                .select_related("leader")
                .prefetch_related("category")
                .all()
            )
        else:
            raise team_exception.TeamKeywordNotMatchError()

        if queryset:
            paginated = self.paginate_queryset(queryset, self.request, view=self)
            serializer = TeamListSerializer(paginated, many=True)
            data = TeamResponse.get_team_list_response(serializer.data, user_id)
            return self.get_paginated_response(data)
        else:
            raise notfound_exception.TeamNotFoundError()
