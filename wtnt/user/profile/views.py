from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

import core.exception.request as exception
from core.permissions import IsApprovedUser
from .service import ProfileService, MyActivityServcie, MyTeamManageService

User = get_user_model()


class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        profile_service = ProfileService(request, **kwargs)
        data = profile_service.process_response_data()

        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        required_field = ["explain", "position"]
        if not (2 <= len(request.data) <= 3):
            raise exception.InvalidRequestError()
        for field in required_field:
            if field not in request.data:
                raise exception.InvalidRequestError()

        profile_service = ProfileService(request, **kwargs)
        profile_service.check_ownership()
        data = profile_service.update_user_info()

        return Response(data, status=status.HTTP_202_ACCEPTED)


class UserTechView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        required_field = ["tech"]
        if len(request.data) != len(required_field):
            raise exception.InvalidRequestError()
        for field in required_field:
            if field not in request.data:
                raise exception.InvalidRequestError()

        profile_service = ProfileService(request, **kwargs)
        profile_service.check_ownership()
        data = profile_service.update_tech_info()

        return Response(data, status=status.HTTP_202_ACCEPTED)


class UserUrlView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        required_field = ["url"]
        if len(request.data) != len(required_field):
            raise exception.InvalidRequestError()
        for field in required_field:
            if field not in request.data:
                raise exception.InvalidRequestError()

        profile_service = ProfileService(request, **kwargs)
        profile_service.check_ownership()
        data = profile_service.update_user_url_info()

        return Response(data, status=status.HTTP_202_ACCEPTED)


class UserMyActivityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        myactivity_service = MyActivityServcie(request, **kwargs)
        data = myactivity_service.get_my_activity()

        return Response(data, status=status.HTTP_200_OK)


class UserManageActivityView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, request, *args, **kwargs):
        myteam_service = MyTeamManageService(request, **kwargs)
        myteam_service.check_ownership()
        data = myteam_service.get_my_teams()

        return Response({"team": data}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        myteam_service = MyTeamManageService(request, **kwargs)
        data = myteam_service.delete_or_leave_team()

        return Response(data, status=status.HTTP_204_NO_CONTENT)


class UserLikeTeamView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, request, *args, **kwargs):
        myactivity_service = MyActivityServcie(request, **kwargs)
        myactivity_service.check_ownership()
        data = myactivity_service.get_like_activity()

        return Response({"team": data}, status=status.HTTP_200_OK)
