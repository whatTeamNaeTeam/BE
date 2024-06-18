import pytest
import requests_mock

from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount

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
                "name": "testuser",
                "avatar_url": "https://avatars.githubusercontent.com/u/123456?v=4",
            },
        )
        yield m


@pytest.fixture
def initial_user():
    User = user.objects.create(
        id=1,
        name="test",
        email="testuser@sample.com",
        image="testimage",
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
