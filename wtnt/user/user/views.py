from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from user.serializers import BaseUserSerializer

User = get_user_model()


class UserManageView(APIView):
    serializer_class = BaseUserSerializer
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = User.objects.filter(is_apporoved=False)
        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data)
