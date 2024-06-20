import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestSocialLogin:
    @pytest.fixture(autouse=True)
    def setup(self, api_client, social_app, github_mock, mock_redis):
        self.api_client = api_client
        self.social_app = social_app
        self.github_mock = github_mock
        self.mock_redis = mock_redis

    def test_github_initial_register(self):
        url = reverse("github-login")
        data = {"access_token": "fake-access-token"}
        response = self.api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK

        response_data = response.data

        assert "registered" in response_data
        assert not response_data["registered"]
        assert "user" not in response_data

    def test_github_login(self, registered_user):
        url = reverse("github-login")
        data = {"access_token": "fake-access-token"}
        response = self.api_client.post(url, data, foramt="json")
        assert response.status_code == status.HTTP_200_OK

        response_data = response.data

        assert response_data["registered"]
        assert response_data["user"]["name"] == "test"

    def test_github_finish(self, initial_user, initial_socialaccount, setup_email_code):
        url = reverse("github-finish")
        data = {
            "email": "testuser@gmail.com",
            "student_num": 111111111,
            "name": "test",
            "position": "test",
            "code": "test",
        }
        assert "test" == self.mock_redis.get("testuser@gmail.com").decode()
        self.api_client.force_authenticate(user=initial_user)
        response = self.api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        responsed_user_data = response.data["user"]

        assert "test" == responsed_user_data["name"]
        assert 111111111 == responsed_user_data["student_num"]
        assert 1 == responsed_user_data["id"]
        assert self.mock_redis.get("testuser@gmail.com") is None

    def test_github_finish_failed_by_email_code(self, initial_user, initial_socialaccount, setup_email_code):
        url = reverse("github-finish")
        data = {
            "email": "testuser@gmail.com",
            "student_num": 111111111,
            "name": "test",
            "position": "test",
            "code": "wrong",
        }
        self.api_client.force_authenticate(user=initial_user)
        response = self.api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_github_finish_failed_by_wrong_data(self, initial_user, initial_socialaccount, setup_email_code):
        url = reverse("github-finish")
        data = {
            "email": "testuser@gmail.com",
            "student_num": 111111111,
            "name": "verylongtestname",
            "position": "test",
            "code": "test",
        }
        self.api_client.force_authenticate(user=initial_user)
        response = self.api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_github_finish_failed_by_missing_data(self, initial_user, initial_socialaccount, setup_email_code):
        url = reverse("github-finish")
        data = {
            "email": "testuser@gmail.com",
            "student_num": 111111111,
            "position": "test",
            "code": "test",
        }
        self.api_client.force_authenticate(user=initial_user)
        response = self.api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_github_finish_failed_by_wrong_type_data(self, initial_user, initial_socialaccount, setup_email_code):
        url = reverse("github-finish")
        data = {
            "email": "testuser@gmail.com",
            "student_num": "test",
            "name": "test",
            "position": "test",
            "code": "test",
        }
        self.api_client.force_authenticate(user=initial_user)
        response = self.api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
