import os

import pytest
from django.test import Client
from rest_framework import status

from apps.users.models import User, UserRole

SCHEMA_URLS = ['/api/schema/', '/api/schema/swagger-ui/', '/api/schema/redoc/']


@pytest.fixture
def staff_user(db):
    """Return a staff user able to log in via Django session."""
    return User.objects.create_user(
        email=os.getenv('TEST_STAFF_EMAIL'),
        password=os.getenv('TEST_USER_PASSWORD'),
        username='staff_member',
        role=UserRole.LESSOR,
        is_staff=True,
    )


@pytest.fixture
def regular_user(db):
    """Return a non-staff user able to log in via Django session."""
    return User.objects.create_user(
        email=os.getenv('TEST_TENANT_EMAIL'),
        password=os.getenv('TEST_USER_PASSWORD'),
        username='regular_member',
        role=UserRole.TENANT,
    )


@pytest.mark.django_db
class TestSchemaAccess:
    """The OpenAPI schema and its docs UIs must only be reachable by staff via session login.

    Note: with SessionAuthentication as the only authenticator, DRF always denies
    with 403 (not 401), because SessionAuthentication has no WWW-Authenticate
    challenge to offer — this is documented, expected DRF behavior.
    """

    @pytest.mark.parametrize('url', SCHEMA_URLS)
    def test_anonymous_cannot_access_schema_403(self, url):
        """An anonymous visitor must not be able to view the API schema or its docs."""
        response = Client().get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('url', SCHEMA_URLS)
    def test_authenticated_non_staff_cannot_access_schema_403(self, url, regular_user):
        """A logged-in but non-staff user must not be able to view the schema."""
        client = Client()
        client.force_login(regular_user)
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize('url', SCHEMA_URLS)
    def test_staff_can_access_schema_200(self, url, staff_user):
        """A staff user logged in via session must be able to view the schema."""
        client = Client()
        client.force_login(staff_user)
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_jwt_bearer_token_does_not_grant_schema_access(self, lessor_client):
        """A JWT bearer token must not authenticate schema requests (session-only by design)."""
        client, _ = lessor_client
        response = client.get('/api/schema/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
