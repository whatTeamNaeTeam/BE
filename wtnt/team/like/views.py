from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

import core.exception.request as exception
from core.permissions import IsApprovedUser
from .service import LikeService


class TeamLikeView(APIView):
    permission_classes = [IsApprovedUser]

    def post(self, request, *args, **kwargs):
        required_field = ["version"]
        if len(request.data) != len(required_field):
            raise exception.InvalidRequestError()
        for field in required_field:
            if field not in request.data:
                raise exception.InvalidRequestError()

        like_service = LikeService(request, **kwargs)
        data = like_service.like()

        return Response(data, status=status.HTTP_202_ACCEPTED)
