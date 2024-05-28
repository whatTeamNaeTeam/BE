from django.contrib.auth import get_user_model

from core.service import BaseService
from core.exceptions import NotFoundException, IsNotOwner, SerializerNotValidException
from user.models import UserUrls, UserTech
from user.serializers import UserUrlSerializer, UserTechSerializer, UserProfileSerializer
from .utils import make_data, make_url_data, make_tech_data

User = get_user_model()


class ProfileService(BaseService):
    def process_response_data(self):
        user_id = self.kwargs.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            url = self.get_url_data(user_id)
            tech = self.get_tech_data(user_id)
            user_serializer = UserProfileSerializer(user)

            return make_data(user_serializer.data, url, tech, user_id)
        except User.DoesNotExist:
            raise NotFoundException()

    def get_url_data(self, user_id):
        try:
            url = UserUrls.objects.get(user_id=user_id)
            response = UserUrlSerializer(url)
        except UserUrls.DoesNotExist:
            response = None

        return response

    def get_tech_data(self, user_id):
        try:
            tech = UserTech.objects.get(user_id=user_id)
            response = UserTechSerializer(tech)
        except UserTech.DoesNotExist:
            response = None

        return response

    def update_user_info(self):
        user = self.request.user
        explain = self.request.data.get("explain")
        position = self.request.data.get("position")

        serializer = UserProfileSerializer(user, data={"explain": explain, "position": position}, partial=True)

        if serializer.is_valid():
            serializer.save()
            return {"explain": explain, "position": position}

        raise SerializerNotValidException(detail=SerializerNotValidException.get_detail(serializer.errors))

    def check_ownership(self):
        owner_id = self.kwargs.get("user_id")
        user_id = self.request.user.id

        if owner_id != user_id:
            raise IsNotOwner()

    def update_user_url_info(self):
        owner_id = self.kwargs.get("user_id")
        user_id = self.request.user.id
        url = self.request.data.get("url")

        user_url = UserUrls.objects.get(user_id=user_id)
        if user_url:
            serializer = self.serializer_class(user_url, data={"url": url}, partial=True)
        else:
            data = {"user_id": owner_id, "url": url}
            serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            data = make_url_data(serializer.data)
            return data

        raise SerializerNotValidException(detail=SerializerNotValidException.get_detail(serializer.errors))

    def update_tech_info(self):
        owner_id = self.kwargs.get("user_id")
        user_id = self.request.user.id
        tech = self.request.data.get("tech")

        user_tech = UserTech.objects.get(user_id=user_id)
        if user_tech:
            serializer = self.serializer_class(user_tech, data={"tech": tech}, partial=True)
        else:
            data = {"user_id": owner_id, "tech": tech}
            serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()
            data = make_tech_data(serializer.data)
            return data
