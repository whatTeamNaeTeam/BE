from django.contrib.auth import get_user_model

from core.exceptions import NotFoundError
from core.pagenations import ListPagenationSize10
from core.service import BaseService
from admin.serializers import ApproveUserSerializer

User = get_user_model()


class AdminUserService(BaseService, ListPagenationSize10):
    def get_not_approved_users(self):
        try:
            queryset = User.objects.filter(is_approved=False, is_superuser=False)
            serializer = ApproveUserSerializer(queryset, many=True)
            return serializer.data

        except User.DoesNotExist:
            raise NotFoundError()

    def approve_users(self):
        user_ids = [int(id) for id in self.request.data.get("ids").split(",")]
        cnt = User.objects.filter(id__in=user_ids).update(is_approved=True)
        if cnt:
            return {"detail": "Success to update users"}
        else:
            raise NotFoundError()

    def reject_users(self, status):
        user_ids = [int(id) for id in self.request.data.get("ids").split(",")]
        cnt, _ = User.objects.filter(id__in=user_ids, is_approved=status).delete()
        if cnt:
            return {"detail": "Success to reject users"}
        else:
            raise NotFoundError()

    def get_approved_users(self):
        queryset = User.objects.filter(is_approved=True, is_superuser=False).order_by("student_num")
        paginated = self.paginate_queryset(queryset, self.request, view=self)
        serializer = ApproveUserSerializer(paginated, many=True)

        return self.get_paginated_response(serializer.data)
