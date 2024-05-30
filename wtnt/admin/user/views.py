from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from django.db.models import Q

from core.pagenations import ListPagenationSize10
from admin.serializers import ApproveUserSerializer
from .service import AdminUserService

User = get_user_model()


class UserManageView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        admin_service = AdminUserService(request)
        data = admin_service.get_not_approved_users()

        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        admin_service = AdminUserService(request)
        data = admin_service.approve_users()

        return Response(data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, *args, **kwargs):
        admin_service = AdminUserService(request)
        data = admin_service.reject_users(status=False)

        return Response(data, status=status.HTTP_204_NO_CONTENT)


class UserDeleteView(APIView, ListPagenationSize10):
    serializer_class = ApproveUserSerializer
    permission_classes = [IsAdminUser]

    def get(self, request):
        admin_service = AdminUserService(request)
        return admin_service.get_approved_users()

    def delete(self, request, *args, **kwargs):
        admin_service = AdminUserService(request)
        data = admin_service.reject_users(status=True)

        return Response(data, status=status.HTTP_204_NO_CONTENT)


class UserSearchView(APIView, ListPagenationSize10):
    permission_classes = [IsAdminUser]
    serializer_class = ApproveUserSerializer

    def get(self, request, *args, **kwargs):
        keyword = request.query_params.get("keyword")
        search_filter = request.query_params.get("filter")

        try:
            if search_filter == "name":
                queryset = User.objects.filter(Q(name__icontains=keyword), is_approved=True).order_by("student_num")
            elif search_filter == "student_num":
                queryset = User.objects.filter(Q(student_num__icontains=keyword), is_approved=True).order_by(
                    "student_num"
                )
            elif search_filter == "position":
                queryset = User.objects.filter(Q(position__icontains=keyword), is_approved=True).order_by("student_num")
            else:
                return Response({"error": "No Filter"}, status=status.HTTP_400_BAD_REQUEST)

            paginated = self.paginate_queryset(queryset, request, view=self)
            serializer = self.serializer_class(paginated, many=True)

            return self.get_paginated_response(serializer.data)

        except User.DoesNotExist:
            return Response({"error": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)
