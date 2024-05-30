from admin.serializers import ApproveTeamSerializer
from core.exceptions import NotFoundError
from core.pagenations import ListPagenationSize10
from core.service import BaseService
from team.models import Team


class AdminTeamService(BaseService, ListPagenationSize10):
    def get_not_approved_team(self):
        try:
            queryset = Team.objects.filter(is_approved=False, is_superuser=False)
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
        cnt, _ = Team.objects.filter(id__in=team_ids, is_approved=status).delete()
        if cnt:
            return {"detail": "Success to reject teams"}
        else:
            raise NotFoundError()

    def get_approved_teams(self):
        queryset = Team.objects.filter(is_approved=True).order_by("id")
        paginated = self.paginate_queryset(queryset, self.request, view=self)
        serializer = ApproveTeamSerializer(paginated, many=True)

        return self.get_paginated_response(serializer.data)
