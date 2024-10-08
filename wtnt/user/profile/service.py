from django.contrib.auth import get_user_model
from django.db.models import Count
from django.core.cache import cache

import core.exception.notfound as notfound_exception
import core.exception.team as team_exception
from core.service import BaseServiceWithCheckOwnership, BaseServiceWithCheckLeader
from user.models import UserUrls, UserTech
from team.models import Team, TeamApply, TeamUser, Likes, TeamTech
from user.serializers import (
    UserUrlSerializer,
    UserTechSerializer,
    UserProfileSerializer,
    UserSerializerOnTeamManageDetail,
)
from team.serializers import TeamListSerializer, TeamManageActivitySerializer
from core.utils.profile import ProfileResponse
from core.utils.team import TeamResponse
from core.utils.s3 import S3Utils

User = get_user_model()


class ProfileService(BaseServiceWithCheckOwnership):
    def get_profile_data_from_id(self, user_id):
        try:
            user = User.objects.select_related("userurls", "usertech").get(id=user_id)
            try:
                user_urls = ProfileResponse.make_url_data(user.userurls.url.decode())
            except UserUrls.DoesNotExist:
                user_urls = []

            try:
                user_tech = ProfileResponse.make_tech_data(user.usertech.tech.decode())
            except UserTech.DoesNotExist:
                user_tech = []

            user_serializer = UserProfileSerializer(user)

            return ProfileResponse.make_cached_data(user_serializer.data, user_urls, user_tech)
        except User.DoesNotExist:
            raise notfound_exception.UserNotFoundError()

    def process_response_data(self):
        user_id = self.kwargs.get("user_id")
        owner_id = self.request.user.id
        cache_key = f"user_profile_{user_id}"

        user_data = cache.get(cache_key)

        if user_data is None:
            user_data = self.get_profile_data_from_id(user_id)
            cache.set(cache_key, user_data, timeout=60 * 5)

        return ProfileResponse.make_data(user_data, owner_id)

    def update_user_info(self):
        user = self.request.user
        explain = self.request.data.get("explain")
        position = self.request.data.get("position")
        image = self.request.FILES.get("image", None)

        url = S3Utils.upload_user_image_on_s3(user.id, image) if image is not None else None
        data = {"explain": explain, "position": position}
        if url is not None:
            data["image"] = url
        serializer = UserProfileSerializer(user, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            cache_key = f"user_profile_{user.id}"
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                cached_data["profile"]["explain"] = explain
                cached_data["profile"]["position"] = position
                if url is not None:
                    cached_data["profile"]["image_url"] = url + "image.jpg"
                cache.set(cache_key, cached_data, timeout=60 * 5)

            return {
                "explain": explain,
                "position": position,
                **({"image_url": url + "image.jpg"} if url is not None else {}),
            }

    def update_user_url_info(self):
        owner_id = self.kwargs.get("user_id")
        user_id = self.request.user.id
        url = self.request.data.get("url")

        try:
            user_url = UserUrls.objects.get(user_id=user_id)
            if url == "":
                user_url.delete()
                return {"urls": []}
            serializer = UserUrlSerializer(user_url, data={"url": url}, partial=True)
        except UserUrls.DoesNotExist:
            data = {"user_id": owner_id, "url": url}
            serializer = UserUrlSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            data = ProfileResponse.make_url_data(serializer.data["url"])

            cache_key = f"user_profile_{user_id}"
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                cached_data["url"] = data
                cache.set(cache_key, cached_data, timeout=60 * 5)

            return data

    def update_tech_info(self):
        owner_id = self.kwargs.get("user_id")
        user_id = self.request.user.id
        tech = self.request.data.get("tech")

        try:
            user_tech = UserTech.objects.get(user_id=user_id)
            if tech == "":
                user_tech.delete()
                return {"tech": []}
            serializer = UserTechSerializer(user_tech, data={"tech": tech}, partial=True)
        except UserTech.DoesNotExist:
            data = {"user_id": owner_id, "tech": tech}
            serializer = UserTechSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            data = ProfileResponse.make_tech_data(serializer.data["tech"])

            cache_key = f"user_profile_{user_id}"
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                cached_data["tech"] = data
                cache.set(cache_key, cached_data, timeout=60 * 5)

            return data


class MyActivityServcie(BaseServiceWithCheckOwnership):
    def get_my_activity(self):
        owner_id = self.kwargs.get("user_id")
        user_id = self.request.user.id
        keyword = self.request.query_params.get("keyword")

        if keyword == "apply":
            team_ids = TeamApply.objects.filter(user_id=owner_id, is_approved=False).values_list("team_id", flat=True)
            team_data = Team.objects.filter(id__in=team_ids).select_related("leader").prefetch_related("category")
        else:
            team_ids = TeamUser.objects.filter(user_id=owner_id).values_list("team_id", flat=True)
            if keyword == "accomplished":
                team_data = (
                    Team.objects.filter(id__in=team_ids, is_accomplished=True, is_approved=True)
                    .select_related("leader")
                    .prefetch_related("category")
                )
            elif keyword == "inprogress":
                team_data = (
                    Team.objects.filter(id__in=team_ids, is_accomplished=False, is_approved=True)
                    .select_related("leader")
                    .prefetch_related("category")
                )
            else:
                raise team_exception.TeamKeywordNotMatchError()

        serializer = TeamListSerializer(team_data, many=True)
        teams = TeamResponse.get_team_list_response(serializer.data, user_id)
        data = ProfileResponse.make_activity_data(teams, owner_id, user_id)

        return data

    def get_like_activity(self):
        owner_id = self.request.user.id

        like_team_ids = Likes.objects.filter(user_id=owner_id).values_list("team_id", flat=True)
        team_data = Team.objects.filter(id__in=like_team_ids).select_related("leader").prefetch_related("category")
        serializer = TeamListSerializer(team_data, many=True)
        data = TeamResponse.get_team_list_response(serializer.data, owner_id)

        return data


class MyTeamManageService(BaseServiceWithCheckOwnership, BaseServiceWithCheckLeader):
    def get_my_teams(self):
        owner_id = self.kwargs.get("user_id")
        user_id = self.request.user.id

        team_users = TeamUser.objects.filter(user_id=owner_id).values("team_id").annotate(member_count=Count("team_id"))
        team_ids = [team["team_id"] for team in team_users]
        member_counts = [team["member_count"] for team in team_users]

        team_data = Team.objects.filter(id__in=team_ids).select_related("leader")
        serializer = TeamManageActivitySerializer(team_data, many=True)
        data = TeamResponse.get_team_list_response(serializer.data, user_id, is_manage=True, count=member_counts)

        return data

    def delete_team(self):
        team_id = self.kwargs.get("user_id")
        user_id = self.request.user.id

        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise notfound_exception.TeamNotFoundError()
        self.check_leader(user_id, team.leader.id)
        S3Utils.delete_team_image_on_s3(team.uuid)
        team.delete()

        return {"detail": "Success to delete team"}

    def leave_team(self):
        team_id = self.kwargs.get("user_id")
        user_id = self.request.user.id

        try:
            team_user = TeamUser.objects.get(team_id=team_id, user_id=user_id)
            team_tech = TeamTech.objects.get(tech=team_user.tech, team_id=team_id)
        except TeamUser.DoesNotExist:
            raise notfound_exception.TeamUserNotFoundError()

        team_user.delete()
        team_tech.current_num -= 1
        team_tech.save()

        return {"detail": "Success to leave team"}

    def get_my_team_detail(self):
        team_id = self.kwargs.get("team_id")

        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            raise notfound_exception.TeamNotFoundError()

        team_users = TeamUser.objects.filter(team_id=team_id).select_related("user")
        member_id_tech_dict = {team_user.user.id: team_user.tech for team_user in team_users}

        members = [team_user.user for team_user in team_users]

        serializer = UserSerializerOnTeamManageDetail(members, many=True)
        data = ProfileResponse.make_team_manage_detail_data(serializer.data, team, member_id_tech_dict)

        return data
