from core.exceptions import NotFoundError, ClosedApplyError, DuplicatedApplyError, SerializerNotValidError
from core.service import BaseServiceWithCheckLeader
from core.utils.team import ApplyResponse
from team.models import TeamApply, Team, TeamTech, TeamUser
from team.serializers import TeamApplySerializer


class ApplyService(BaseServiceWithCheckLeader):
    def get_applies(self):
        team_id = self.kwargs.get("team_id")
        user_id = self.request.user.id
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise NotFoundError()
        self.check_leader(user_id, team.leader.id)

        queryset = TeamApply.objects.filter(is_approved=False, team_id=team_id)

        if queryset:
            serializer = TeamApplySerializer(queryset, many=True)
            return serializer.data
        else:
            raise NotFoundError()

    def post_apply(self):
        bio = self.request.data.get("bio", None)
        tech = self.request.data.get("subCategory")
        user_id = self.request.user.id
        team_id = self.kwargs.get("team_id")

        teamTech = TeamTech.objects.get(team_id=team_id, tech=tech)
        if teamTech.need_num <= teamTech.current_num:
            raise ClosedApplyError()

        apply_data = ApplyResponse.make_data(user_id, team_id, bio, tech)
        serializer = TeamApplySerializer(data=apply_data)

        if serializer.is_valid():
            try:
                serializer.save()
            except Exception:
                raise DuplicatedApplyError()

            return serializer.data

        raise SerializerNotValidError(detail=SerializerNotValidError.get_detail(serializer.errors))

    def approve_apply(self):
        apply_id = self.kwargs.get("team_id")
        user_id = self.request.user.id
        try:
            apply = TeamApply.objects.get(id=apply_id)
            team = Team.objects.get(id=apply.team_id)
            team_tech = TeamTech.objects.get(team_id=team.id, tech=apply.tech)
        except TeamApply.DoesNotExist:
            raise NotFoundError()
        except Team.DoesNotExist:
            raise NotFoundError()
        except TeamTech.DoesNotExist:
            raise NotFoundError()

        if team_tech.current_num >= team_tech.need_num:
            raise ClosedApplyError()

        self.check_leader(user_id, team.leader.id)

        serializer = TeamApplySerializer(apply, data={"is_approved": True}, partial=True)
        if serializer.is_valid():
            serializer.save()
            team_tech.current_num += 1
            team_tech.save()

            teamUser = TeamUser(team_id=team.id, user_id=user_id)
            teamUser.save()

            apply.delete()

            return {"detail": "Success to update apply"}

        raise SerializerNotValidError(detail=SerializerNotValidError.get_detail(serializer.errors))

    def reject_apply(self):
        apply_id = self.kwargs.get("team_id")
        user_id = self.request.user.id
        try:
            apply = TeamApply.objects.get(id=apply_id)
            team = Team.objects.get(id=apply.team_id)
        except TeamApply.DoesNotExist:
            raise NotFoundError()
        except Team.DoesNotExist:
            raise NotFoundError()

        self.check_leader(user_id, team.leader.id)
        apply.delete()

        return {"detail": "Success to reject apply"}
