from django.contrib.auth import get_user_model

from core.service import BaseService
from core.exceptions import NotFoundError, IsNotOwnerError, SerializerNotValidError, KeywordNotMatchError
from user.models import UserUrls, UserTech
from team.models import Team, TeamApply, TeamUser, Likes
from user.serializers import UserUrlSerializer, UserTechSerializer, UserProfileSerializer
from team.serializers import TeamListSerializer, TeamManageActivitySerializer
from core.utils.profile import ProfileResponse
from core.utils.team import make_team_list

User = get_user_model()


class BaseServiceWithCheckOwnership(BaseService):
    def check_ownership(self):
        owner_id = self.kwargs.get("user_id")
        user_id = self.request.user.id

        if owner_id != user_id:
            raise IsNotOwnerError()


class ProfileService(BaseServiceWithCheckOwnership):
    def process_response_data(self):
        user_id = self.kwargs.get("user_id")
        owner_id = self.request.user.id

        try:
            user = User.objects.get(id=user_id)
            url = self.get_url_data(user_id)
            tech = self.get_tech_data(user_id)
            user_serializer = UserProfileSerializer(user)

            return ProfileResponse.make_data(user_serializer.data, url, tech, owner_id)
        except User.DoesNotExist:
            raise NotFoundError()

    def get_url_data(self, user_id):
        try:
            url = UserUrls.objects.get(user_id=user_id)
            response = UserUrlSerializer(url)
        except UserUrls.DoesNotExist:
            response = None

        return response

    def get_tech_data(self, user_id):
        try:
            tech = UserTech.objects.get(user_id=user_id)
            response = UserTechSerializer(tech)
        except UserTech.DoesNotExist:
            response = None

        return response

    def update_user_info(self):
        user = self.request.user
        explain = self.request.data.get("explain")
        position = self.request.data.get("position")

        serializer = UserProfileSerializer(user, data={"explain": explain, "position": position}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return {"explain": explain, "position": position}

        raise SerializerNotValidError(detail=SerializerNotValidError.get_detail(serializer.errors))

    def update_user_url_info(self):
        owner_id = self.kwargs.get("user_id")
        user_id = self.request.user.id
        url = self.request.data.get("url")

        user_url = UserUrls.objects.get(user_id=user_id)
        if user_url:
            serializer = self.serializer_class(user_url, data={"url": url}, partial=True)
        else:
            data = {"user_id": owner_id, "url": url}
            serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            data = ProfileResponse.make_url_data(serializer.data)
            return data

        raise SerializerNotValidError(detail=SerializerNotValidError.get_detail(serializer.errors))

    def update_tech_info(self):
        owner_id = self.kwargs.get("user_id")
        user_id = self.request.user.id
        tech = self.request.data.get("tech")

        user_tech = UserTech.objects.get(user_id=user_id)
        if user_tech:
            serializer = self.serializer_class(user_tech, data={"tech": tech}, partial=True)
        else:
            data = {"user_id": owner_id, "tech": tech}
            serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            data = ProfileResponse.make_tech_data(serializer.data)
            return data


class MyActivityServcie(BaseServiceWithCheckOwnership):
    def get_my_activity(self):
        owner_id = self.kwargs.get("user_id")
        user_id = self.request.user.id
        keyword = self.request.query_params.get("keyword")

        if keyword == "apply":
            team_ids = TeamApply.objects.filter(user_id=owner_id, is_approved=False).values_list("team_id", flat=True)
            team_data = Team.objects.filter(id__in=team_ids)
        else:
            team_ids = TeamUser.objects.filter(user_id=owner_id).values_list("team_id", flat=True)
            if keyword == "accomplished":
                team_data = Team.objects.filter(id__in=team_ids, is_accomplished=True, is_approved=True)
            elif keyword == "inprogress":
                team_data = Team.objects.filter(id__in=team_ids, is_accomplished=False, is_approved=True)
            else:
                raise KeywordNotMatchError()

        serializer = TeamListSerializer(team_data, many=True)
        teams = make_team_list(serializer.data, user_id)
        data = ProfileResponse.make_activity_data(teams, owner_id, user_id)

        return data

    def get_like_activity(self):
        owner_id = self.request.user.id

        like_team_ids = Likes.objects.filter(user_id=owner_id).values_list("team_id", flat=True)
        team_data = Team.objects.filter(id__in=like_team_ids)
        serializer = TeamListSerializer(team_data, many=True)
        data = make_team_list(serializer.data, owner_id)

        return data


class MyTeamManageService(BaseServiceWithCheckOwnership):
    def get_my_teams(self):
        owner_id = self.kwargs.get("user_id")
        user_id = self.request.user.id

        team_ids = TeamUser.objects.filter(user_id=owner_id).values_list("team_id", flat=True)
        team_data = Team.objects.filter(id__in=team_ids)
        serializer = TeamManageActivitySerializer(team_data, many=True)
        data = make_team_list(serializer.data, user_id, is_manage=True)

        return data
