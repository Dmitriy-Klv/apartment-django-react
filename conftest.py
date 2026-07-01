import os

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User, UserRole


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD')


@pytest.fixture
def lessor_client(db):
    """Return (APIClient, user) for an authenticated lessor."""
    user = User.objects.create_user(
        email=os.getenv('TEST_LESSOR_EMAIL'),
        password=TEST_USER_PASSWORD,
        first_name='Jane',
        last_name='Smith',
        role=UserRole.LESSOR,
    )
    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(token.access_token)}')
    return client, user


@pytest.fixture
def lessor_client_2(db):
    """Return (APIClient, user) for a second authenticated lessor."""
    user = User.objects.create_user(
        email=os.getenv('TEST_LESSOR2_EMAIL'),
        password=TEST_USER_PASSWORD,
        first_name='Other',
        last_name='Lessor',
        role=UserRole.LESSOR,
    )
    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(token.access_token)}')
    return client, user


@pytest.fixture
def tenant_client(db):
    """Return (APIClient, user) for an authenticated tenant."""
    user = User.objects.create_user(
        email=os.getenv('TEST_TENANT_EMAIL'),
        password=TEST_USER_PASSWORD,
        first_name='John',
        last_name='Doe',
        role=UserRole.TENANT,
    )
    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(token.access_token)}')
    return client, user
