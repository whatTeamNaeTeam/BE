import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestSocialLogin:
    @pytest.fixture(autouse=True)
    def setup(self, api_client, social_app, github_mock):
        self.api_client = api_client
        self.social_app = social_app
        self.github_mock = github_mock

    def test_github_initial_register(self):
        url = reverse("github-login")
        data = {"access_token": "fake-access-token"}
        response = self.api_client.post(url, data, format="json")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

        response_data = response.data

        assert "registered" in response_data
        assert "user" not in response_data
