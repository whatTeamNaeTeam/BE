import core.exception.notfound as notfound_exception
import core.exception.apply as apply_exception
from core.service import BaseServiceWithCheckLeader
from core.utils.team import ApplyResponse
from django.db import IntegrityError
from team.models import TeamApply, Team, TeamTech, TeamUser
from team.serializers import TeamApplySerializer


class ApplyService(BaseServiceWithCheckLeader):
    def get_applies(self):
        team_id = self.kwargs.get("team_id")
        user_id = self.request.user.id
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise notfound_exception.TeamNotFoundError()
        self.check_leader(user_id, team.leader.id)

        queryset = TeamApply.objects.filter(team_id=team_id)

        if queryset:
            serializer = TeamApplySerializer(queryset, many=True)
            return serializer.data
        else:
            raise notfound_exception.ApplyNotFoundError()

    def post_apply(self):
        bio = self.request.data.get("bio", "열심히 하겠습니다!")
        user_id = self.request.user.id
        tech_id = self.kwargs.get("team_id")
        try:
            teamTech = TeamTech.objects.get(id=tech_id)
        except TeamTech.DoesNotExist:
            raise notfound_exception.TechNotFoundError()

        if teamTech.need_num <= teamTech.current_num:
            raise apply_exception.ClosedApplyError()

        apply_data = ApplyResponse.make_data(user_id, teamTech.team.id, bio, teamTech.tech)
        serializer = TeamApplySerializer(data=apply_data)

        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                raise apply_exception.DuplicatedApplyError()

            return serializer.data

    def approve_apply(self):
        apply_id = self.kwargs.get("team_id")
        user_id = self.request.user.id
        try:
            apply = TeamApply.objects.get(id=apply_id)
            team = Team.objects.get(id=apply.team_id)
            team_tech = TeamTech.objects.get(team_id=team.id, tech=apply.tech)
        except TeamApply.DoesNotExist:
            raise notfound_exception.ApplyNotFoundError()
        except Team.DoesNotExist:
            raise notfound_exception.TeamNotFoundError()
        except TeamTech.DoesNotExist:
            raise notfound_exception.TechNotFoundError()

        if team_tech.current_num >= team_tech.need_num:
            raise apply_exception.ClosedApplyError()

        self.check_leader(user_id, team.leader.id)

        team_tech.current_num += 1
        team_tech.save()

        teamUser = TeamUser(team_id=team.id, user_id=user_id, tech=apply.tech)
        teamUser.save()

        apply.delete()

        return {"detail": "Success to update apply"}

    def reject_apply(self):
        apply_id = self.kwargs.get("team_id")
        user_id = self.request.user.id
        try:
            apply = TeamApply.objects.get(id=apply_id)
            team = Team.objects.get(id=apply.team_id)
        except TeamApply.DoesNotExist:
            raise notfound_exception.ApplyNotFoundError()
        except Team.DoesNotExist:
            raise notfound_exception.TeamNotFoundError()

        self.check_leader(user_id, team.leader.id)
        apply.delete()

        return {"detail": "Success to reject apply"}
