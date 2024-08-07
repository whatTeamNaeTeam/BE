import pytest
import requests_mock

from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

user = get_user_model()


@pytest.fixture
def github_mock():
    with requests_mock.Mocker() as m:
        m.post(
            "https://github.com/login/oauth/access_token",
            json={
                "access_token": "fake-access-token",
                "scope": "",
                "token_type": "bearer",
            },
        )
        m.get(
            "https://api.github.com/user",
            json={
                "id": 123456,
                "login": "testuser",
                "name": "test",
                "avatar_url": "https://avatars.githubusercontent.com/u/123456?v=4",
            },
        )
        yield m


@pytest.fixture
def initial_user():
    User = user.objects.create(id=1, name="test", email="testuser@sample.com", image="testimage", password="testpw")

    return User


@pytest.fixture
def registered_user():
    User = user.objects.create(id=1, name="test", email="testuser@gmail.com", image="testimage/", password="testpw")
    SocialAccount.objects.create(
        id=1,
        provider="github",
        uid=123456,
        last_login=None,
        date_joined=None,
        extra_data={"id": 123456, "login": "testuser", "avatar_url": "testimage/"},
        user_id=1,
    )

    return User


@pytest.fixture
def initial_socialaccount(initial_user):
    SocialAccount.objects.create(
        id=1,
        provider="github",
        last_login=None,
        date_joined=None,
        extra_data={"id": 123456, "login": "testuser", "avatar_url": "testimage/"},
        user_id=1,
    )


@pytest.fixture
def setup_email_code(mock_redis):
    mock_redis.set("testuser@gmail.com", "test")
    yield mock_redis


@pytest.fixture
def access_token(registered_user):
    return AccessToken.for_user(registered_user)


@pytest.fixture
def refresh_token(registered_user):
    return RefreshToken.for_user(registered_user)
