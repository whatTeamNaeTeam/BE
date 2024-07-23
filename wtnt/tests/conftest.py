import pytest
import fakeredis

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from rest_framework.test import APIClient
from unittest.mock import patch


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def social_app(db):
    site = Site.objects.get_current()
    social_app = SocialApp.objects.create(
        provider="github", name="GitHub", client_id="fake-client-id", secret="fake-client-secret"
    )
    social_app.sites.add(site)
    return social_app


@pytest.fixture
def mock_redis():
    mock_redis_client = fakeredis.FakeStrictRedis()
    with patch("core.utils.redis.RedisUtils.client", mock_redis_client):
        yield mock_redis_client
