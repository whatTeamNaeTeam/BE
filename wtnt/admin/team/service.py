from django.contrib.auth import get_user_model

from admin.serializers import ApproveTeamSerializer
from core.exceptions import NotFoundError, KeywordNotMatchError
from core.pagenations import ListPagenationSize10
from core.service import BaseService
from core.utils.s3 import S3Utils
from team.models import Team

User = get_user_model()


class AdminTeamService(BaseService, ListPagenationSize10):
    def get_not_approved_team(self):
        try:
            queryset = Team.objects.filter(is_approved=False)
            serializer = ApproveTeamSerializer(queryset, many=True)
            return serializer.data

        except Team.DoesNotExist:
            raise NotFoundError()

    def approve_teams(self):
        team_ids = [int(id) for id in self.request.data.get("ids").split(",")]
        cnt = Team.objects.filter(id__in=team_ids).update(is_approved=True)
        if cnt:
            return {"detail": "Success to update teams"}
        else:
            raise NotFoundError()

    def reject_teams(self, status):
        team_ids = [int(id) for id in self.request.data.get("ids").split(",")]
        teams = Team.objects.filter(id__in=team_ids, is_approved=status)
        if status:
            for team in teams:
                S3Utils.delete_team_image_on_s3(team.title)
        cnt, _ = teams.delete()
        if cnt:
            return {"detail": "Success to reject teams"}
        else:
            raise NotFoundError()

    def get_approved_teams(self):
        queryset = Team.objects.filter(is_approved=True).order_by("id")
        paginated = self.paginate_queryset(queryset, self.request, view=self)
        serializer = ApproveTeamSerializer(paginated, many=True)

        return self.get_paginated_response(serializer.data)

    def serach_teams(self):
        keyword = self.request.query_params.get("keyword")
        search_filter = self.request.query_params.get("filter")

        if search_filter == "name":
            queryset = Team.objects.search_by_name(name=keyword)
        elif search_filter == "genre":
            queryset = Team.objects.search_by_genre(genre=keyword)
        elif search_filter == "leader":
            leader_ids = User.objects.search_by_name(name=keyword).values_list("id", flat=True)
            queryset = Team.objects.search_by_leader_ids(leader_ids=leader_ids)
        else:
            raise KeywordNotMatchError

        if not queryset:
            raise NotFoundError()

        paginated = self.paginate_queryset(queryset, self.request, view=self)
        serializer = ApproveTeamSerializer(paginated, many=True)

        return self.get_paginated_response(serializer.data)
