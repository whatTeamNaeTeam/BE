from django.contrib.auth import get_user_model
from django.core.cache import cache

import core.exception.notfound as notfound_exception
import core.exception.team as team_exception
from core.pagenations import UserListPagenationSize10
from core.service import BaseService
from core.utils.s3 import S3Utils
from admin.serializers import ApproveUserSerializer

User = get_user_model()


class AdminUserService(BaseService, UserListPagenationSize10):
    def get_not_approved_users(self):
        queryset = User.objects.filter(is_approved=False, is_superuser=False)
        if queryset:
            serializer = ApproveUserSerializer(queryset, many=True)
            return serializer.data

        return []

    def approve_users(self):
        user_ids = [int(id) for id in self.request.data.get("ids").split(",")]
        cnt = User.objects.filter(id__in=user_ids).update(is_approved=True)
        if cnt:
            cache_count = cache.get("cache_count_user")
            if cache_count:
                cache_count += cnt
                cache.set("cache_count_user", cache_count, timeout=60 * 5)
            return {"detail": "Success to update users"}
        else:
            raise notfound_exception.UserNotFoundError()

    def reject_users(self, status):
        user_ids = [int(id) for id in self.request.data.get("ids").split(",")]
        if status:
            for user_id in user_ids:
                S3Utils.delete_user_image_on_s3(user_id)
        cnt, _ = User.objects.filter(id__in=user_ids, is_approved=status).delete()
        if cnt:
            return {"detail": "Success to reject users"}
        else:
            raise notfound_exception.UserNotFoundError()

    def get_approved_users(self):
        queryset = User.objects.filter(is_approved=True, is_superuser=False).order_by("student_num")
        paginated = self.paginate_queryset(queryset, self.request, view=self)
        serializer = ApproveUserSerializer(paginated, many=True)

        return self.get_paginated_response(serializer.data)

    def search_users(self):
        keyword = self.request.query_params.get("keyword")
        search_filter = self.request.query_params.get("filter")

        if search_filter == "name":
            queryset = User.objects.search_by_name(name=keyword)
        elif search_filter == "student_num":
            queryset = User.objects.search_by_student_num(student_num=keyword)
        elif search_filter == "position":
            queryset = User.objects.search_by_position(position=keyword)
        else:
            raise team_exception.TeamKeywordNotMatchError()

        paginated = self.paginate_queryset(queryset, self.request, view=self, is_search=True)
        serializer = ApproveUserSerializer(paginated, many=True)

        return self.get_paginated_response(serializer.data)
