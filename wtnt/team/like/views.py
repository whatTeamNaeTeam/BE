from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsApprovedUser
from .service import LikeService


class TeamLikeView(APIView):
    permission_classes = [IsApprovedUser]

    def post(self, request, *args, **kwargs):
        like_service = LikeService(request, **kwargs)
        data = like_service.like()

        return Response(data, status=status.HTTP_202_ACCEPTED)
