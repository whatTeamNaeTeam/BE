from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model

from user.serializers import ApproveUserSerializer

User = get_user_model()


class UserManageView(APIView):
    serializer_class = ApproveUserSerializer
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = User.objects.filter(is_approved=False)
        if queryset:
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "No Content"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        user = User.objects.get(id=user_id)

        serializer = ApproveUserSerializer(user, data={"is_approved": True}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True}, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = ApproveUserSerializer

    def get(self, request):
        queryset = User.objects.filter(is_approved=True, is_superuser=False)
        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            user.delete()

            return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)

        except User.DoesNotExist:
            return Response({"error": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)
