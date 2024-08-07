import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestJWT:
    @pytest.fixture(autouse=True)
    def setup(self, api_client, mock_redis):
        self.api_client = api_client
        self.mock_redis = mock_redis

    def test_token_refresh(self, access_token, refresh_token):
        url = reverse("token-refresh")

        self.mock_redis.set("1", str(refresh_token))

        headers = {"Authorization": f"Bearer {str(access_token)}", "Content-Type": "application/json"}
        response = self.api_client.post(url, {}, format="json", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.headers

    def test_token_refresh_failed(self, access_token):
        url = reverse("token-refresh")

        headers = {"Authorization": f"Bearer {str(access_token)}", "Content-Type": "application/json"}

        response = self.api_client.post(url, {}, format="json", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authencation_failed(self, registered_user):
        user_id = registered_user.id

        url = reverse("profile-team-manage", args=[user_id])  # Random View Need Authentication

        response = self.api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authentication_failed_by_permission(self, registered_user, access_token):
        user_id = registered_user.id

        headers = {"Authorization": f"Bearer {str(access_token)}", "Content-Type": "application/json"}
        url = reverse("profile-team-manage", args=[user_id])

        response = self.api_client.get(url, headers=headers)

        assert response.status_code == status.HTTP_403_FORBIDDEN
