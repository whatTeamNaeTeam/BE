from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

import core.exception.request as exception
from core.permissions import IsApprovedUser
from .service import ApplyService


class TeamApplyView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, request, *args, **kwargs):
        apply_service = ApplyService(request, **kwargs)
        data = apply_service.get_applies()

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        required_field = ["bio"]
        if len(request.data) != len(required_field):
            raise exception.InvalidRequestError()
        for field in required_field:
            if field not in request.data:
                raise exception.InvalidRequestError()

        apply_service = ApplyService(request, **kwargs)
        data = apply_service.post_apply()

        return Response(data, status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        apply_service = ApplyService(request, **kwargs)
        data = apply_service.approve_apply()

        return Response(data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, *args, **kwargs):
        apply_service = ApplyService(request, **kwargs)
        data = apply_service.reject_apply()

        return Response(data, status=status.HTTP_204_NO_CONTENT)
