from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model

from core.pagenations import ListPagenationSize10
from admin.serializers import ApproveUserSerializer

User = get_user_model()


class UserManageView(APIView):
    serializer_class = ApproveUserSerializer
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = User.objects.filter(is_approved=False, is_superuser=False)
        if queryset:
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No Content"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        user_id = [int(id) for id in request.data.get("ids").split(",")]
        user = User.objects.filter(id__in=user_id)
        user.update(is_approved=True)

        return Response({"success": True}, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, *args, **kwargs):
        user_id = [int(id) for id in request.data.get("ids").split(",")]
        try:
            user = User.objects.filter(id__in=user_id)
            user.delete()

            return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)

        except User.DoesNotExist:
            return Response({"error": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)


class UserDeleteView(APIView, ListPagenationSize10):
    serializer_class = ApproveUserSerializer
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = User.objects.filter(is_approved=True, is_superuser=False).order_by("student_num")
        paginated = self.paginate_queryset(queryset, request, view=self)
        serializer = self.serializer_class(paginated, many=True)

        return self.get_paginated_response(serializer.data)

    def delete(self, request, *args, **kwargs):
        user_id = [int(id) for id in request.data.get("ids").split(",")]
        try:
            user = User.objects.filter(id__in=user_id)
            user.delete()

            return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)

        except User.DoesNotExist:
            return Response({"error": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)
