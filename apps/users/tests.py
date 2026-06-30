import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User, UserRole

REGISTER_URL = '/api/v1/auth/register/'
LOGIN_URL = '/api/v1/auth/login/'
LOGOUT_URL = '/api/v1/auth/logout/'
REFRESH_URL = '/api/v1/auth/token/refresh/'
ME_URL = '/api/v1/auth/me/'


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def tenant_payload():
    """Return valid payload for tenant registration."""
    return {
        'email': 'tenant@test.com',
        'password': 'StrongPass123',
        'first_name': 'John',
        'last_name': 'Doe',
        'role': UserRole.TENANT,
    }


@pytest.fixture
def lessor_payload():
    """Return valid payload for lessor registration."""
    return {
        'email': 'lessor@test.com',
        'password': 'StrongPass123',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'role': UserRole.LESSOR,
    }


@pytest.fixture
def tenant_user(db, tenant_payload):
    """Create and return a tenant user in the database."""
    payload = tenant_payload.copy()
    password = payload.pop('password')
    return User.objects.create_user(password=password, **payload)


@pytest.fixture
def lessor_user(db, lessor_payload):
    """Create and return a lessor user in the database."""
    payload = lessor_payload.copy()
    password = payload.pop('password')
    return User.objects.create_user(password=password, **payload)


@pytest.fixture
def auth_tenant(api_client, db, tenant_payload):
    """Register a tenant and return the client authenticated with the access token."""
    response = api_client.post(REGISTER_URL, tenant_payload)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    return api_client, response.data


@pytest.fixture
def auth_lessor(api_client, db, lessor_payload):
    """Register a lessor and return the client authenticated with the access token."""
    response = api_client.post(REGISTER_URL, lessor_payload)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    return api_client, response.data


@pytest.mark.django_db
class TestRegister:

    def test_register_tenant_returns_201(self, api_client, tenant_payload):
        """Valid tenant registration must return 201 with tokens and user data."""
        response = api_client.post(REGISTER_URL, tenant_payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == tenant_payload['email']
        assert response.data['user']['role'] == UserRole.TENANT

    def test_register_lessor_returns_201(self, api_client, lessor_payload):
        """Valid lessor registration must return 201 with correct role."""
        response = api_client.post(REGISTER_URL, lessor_payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['user']['role'] == UserRole.LESSOR

    def test_register_duplicate_email_returns_400(self, api_client, tenant_payload, tenant_user):
        """Registration with an existing email must return 400."""
        response = api_client.post(REGISTER_URL, tenant_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_register_invalid_role_returns_400(self, api_client, tenant_payload):
        """Registration with an unsupported role must return 400."""
        tenant_payload['role'] = 'admin'
        response = api_client.post(REGISTER_URL, tenant_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_short_password_returns_400(self, api_client, tenant_payload):
        """Password shorter than 8 characters must be rejected."""
        tenant_payload['password'] = '123'
        response = api_client.post(REGISTER_URL, tenant_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_fields_returns_400(self, api_client):
        """Empty body must return 400."""
        response = api_client.post(REGISTER_URL, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_creates_user_in_db(self, api_client, tenant_payload):
        """Successful registration must persist the user in the database."""
        api_client.post(REGISTER_URL, tenant_payload)
        assert User.objects.filter(email=tenant_payload['email']).exists()

    def test_register_password_is_hashed(self, api_client, tenant_payload):
        """Stored password must not be a plain-text match."""
        api_client.post(REGISTER_URL, tenant_payload)
        user = User.objects.get(email=tenant_payload['email'])
        assert user.password != tenant_payload['password']


@pytest.mark.django_db
class TestLogin:

    def test_login_valid_credentials_returns_200(self, api_client, tenant_payload, tenant_user):
        """Valid credentials must return 200 with access and refresh tokens."""
        response = api_client.post(LOGIN_URL, {
            'email': tenant_payload['email'],
            'password': tenant_payload['password'],
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == tenant_payload['email']

    def test_login_wrong_password_returns_401(self, api_client, tenant_user):
        """Wrong password must return 401."""
        response = api_client.post(LOGIN_URL, {
            'email': tenant_user.email,
            'password': 'wrongpassword',
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_email_returns_401(self, api_client):
        """Non-existent email must return 401."""
        response = api_client.post(LOGIN_URL, {
            'email': 'nobody@test.com',
            'password': 'SomePass123',
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_fields_returns_400(self, api_client):
        """Empty body must return 400."""
        response = api_client.post(LOGIN_URL, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogout:

    def test_logout_valid_token_returns_204(self, auth_tenant):
        """Logout with a valid refresh token must return 204."""
        client, data = auth_tenant
        response = client.post(LOGOUT_URL, {'refresh': data['refresh']})
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_logout_without_auth_returns_401(self, api_client):
        """Logout without an access token must return 401."""
        response = api_client.post(LOGOUT_URL, {'refresh': 'sometoken'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_blacklisted_token_returns_400(self, auth_tenant):
        """Using the same refresh token twice must return 400 on the second call."""
        client, data = auth_tenant
        client.post(LOGOUT_URL, {'refresh': data['refresh']})
        response = client.post(LOGOUT_URL, {'refresh': data['refresh']})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTokenRefresh:

    def test_refresh_returns_new_access_token(self, auth_tenant):
        """Valid refresh token must return a new access token."""
        _, data = auth_tenant
        client = APIClient()
        response = client.post(REFRESH_URL, {'refresh': data['refresh']})
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_refresh_invalid_token_returns_401(self, api_client):
        """Invalid refresh token must return 401."""
        response = api_client.post(REFRESH_URL, {'refresh': 'invalid.token.here'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestMeEndpoint:

    def test_me_without_token_returns_401(self, api_client):
        """Accessing /me/ without a token must return 401."""
        response = api_client.get(ME_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_with_valid_token_returns_200(self, auth_tenant, tenant_payload):
        """Authenticated user must receive their own profile data."""
        client, _ = auth_tenant
        response = client.get(ME_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == tenant_payload['email']
        assert response.data['role'] == UserRole.TENANT
        assert 'password' not in response.data

    def test_me_lessor_returns_correct_role(self, auth_lessor, lessor_payload):
        """Lessor must see their own role in /me/ response."""
        client, _ = auth_lessor
        response = client.get(ME_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['role'] == UserRole.LESSOR


@pytest.mark.django_db
class TestPermissions:

    def test_islessor_denies_tenant(self, auth_tenant):
        """Tenant role must be correctly stored and differ from lessor."""
        client, data = auth_tenant
        response = client.get(ME_URL)
        assert response.data['role'] == UserRole.TENANT
        assert response.data['role'] != UserRole.LESSOR

    def test_islessor_allows_lessor(self, auth_lessor):
        """Lessor role must be correctly stored."""
        client, data = auth_lessor
        response = client.get(ME_URL)
        assert response.data['role'] == UserRole.LESSOR
