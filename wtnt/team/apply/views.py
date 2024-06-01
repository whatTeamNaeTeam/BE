from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from team.serializers import TeamApplySerializer
from core.permissions import IsApprovedUser
from .service import ApplyService


class TeamApplyView(APIView):
    permission_classes = [IsApprovedUser]
    serializer_class = TeamApplySerializer

    def get(self, request, *args, **kwargs):
        apply_service = ApplyService(request, **kwargs)
        data = apply_service.get_applies()

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
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
