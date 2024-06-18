import pytest

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from rest_framework.test import APIClient


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
