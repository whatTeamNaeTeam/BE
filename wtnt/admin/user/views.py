from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

import core.exception.request as exception
from core.permissions import IsAdminUser
from .service import AdminUserService

User = get_user_model()


class UserManageView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        admin_service = AdminUserService(request)
        data = admin_service.get_not_approved_users()

        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        required_field = ["ids"]
        if len(request.data) != len(required_field):
            raise exception.InvalidRequestError()
        for field in required_field:
            if field not in request.data:
                raise exception.InvalidRequestError()

        admin_service = AdminUserService(request)
        data = admin_service.approve_users()

        return Response(data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, *args, **kwargs):
        required_field = ["ids"]
        if len(request.data) != len(required_field):
            raise exception.InvalidRequestError()
        for field in required_field:
            if field not in request.data:
                raise exception.InvalidRequestError()

        admin_service = AdminUserService(request)
        data = admin_service.reject_users(status=False)

        return Response(data, status=status.HTTP_204_NO_CONTENT)


class UserDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        admin_service = AdminUserService(request)
        return admin_service.get_approved_users()

    def delete(self, request, *args, **kwargs):
        required_field = ["ids"]
        if len(request.data) != len(required_field):
            raise exception.InvalidRequestError()
        for field in required_field:
            if field not in request.data:
                raise exception.InvalidRequestError()

        admin_service = AdminUserService(request)
        data = admin_service.reject_users(status=True)

        return Response(data, status=status.HTTP_204_NO_CONTENT)


class UserSearchView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        admin_service = AdminUserService(request)
        return admin_service.search_users()
