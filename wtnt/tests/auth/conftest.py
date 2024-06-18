import pytest
import requests_mock


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
