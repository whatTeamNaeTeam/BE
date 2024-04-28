from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from user.serializers import UserProfileSerializer, UserTechSerializer, UserUrlSerializer
from user.models import UserTech, UserUrls
from user.utils import profileSerializerHelper

User = get_user_model()


class UserProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            owner_id = request.user.id
        else:
            owner_id = 0
        user_id = kwargs.get("user_id")

        user_queryset = User.objects.get(id=user_id)
        if user_queryset:
            url_queryset = UserUrls.objects.get(user_id=user_id)
            tech_queryset = UserTech.objects.get(user_id=user_id)

            user_serializer = UserProfileSerializer(user_queryset)
            url_serializer = UserUrlSerializer(url_queryset) if url_queryset else None
            tech_serializer = UserTechSerializer(tech_queryset) if tech_queryset else None

            return Response(
                profileSerializerHelper.make_data(owner_id, user_serializer, url_serializer, tech_serializer),
                status=status.HTTP_200_OK,
            )

        return Response({"error": "No Content"}, status=status.HTTP_404_NOT_FOUND)


class UserTechView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserTechSerializer

    def post(self, request, *args, **kwargs):
        owner_id = kwargs.get("user_id")
        user_id = request.user.id
        tech = request.data.get("tech")

        if owner_id != user_id:
            return Response({"error": "It's not an owner"}, status=status.HTTP_403_FORBIDDEN)

        user_tech = UserTech.objects.filter(user_id=user_id).first()

        if user_tech:
            serializer = self.serializer_class(user_tech, data={"tech": tech}, partial=True)

        else:
            data = {"user_id": owner_id, "tech": tech}
            serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({"urls": profileSerializerHelper.make_tech_data(tech)}, status=status.HTTP_202_ACCEPTED)

        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserUrlView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserUrlSerializer

    def post(self, request, *args, **kwargs):
        owner_id = kwargs.get("user_id")
        user_id = request.user.id
        url = request.data.get("url")

        if owner_id != user_id:
            return Response({"error": "It's not an owner"}, status=status.HTTP_403_FORBIDDEN)

        user_url = UserUrls.objects.filter(user_id=user_id).first()

        if user_url:
            serializer = self.serializer_class(user_url, data={"url": url}, partial=True)
        else:
            data = {"user_id": owner_id, "url": url}
            serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({"urls": profileSerializerHelper.make_url_data(url)}, status=status.HTTP_202_ACCEPTED)

        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
