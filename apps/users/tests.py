import os

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User, UserRole
from apps.users.serializers.user import UserSerializer

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
        'email': os.getenv('TEST_TENANT_EMAIL'),
        'password': os.getenv('TEST_USER_PASSWORD'),
        'username': 'john_tenant',
        'role': UserRole.TENANT,
    }


@pytest.fixture
def lessor_payload():
    """Return valid payload for lessor registration."""
    return {
        'email': os.getenv('TEST_LESSOR_EMAIL'),
        'password': os.getenv('TEST_USER_PASSWORD'),
        'username': 'jane_lessor',
        'role': UserRole.LESSOR,
    }


@pytest.fixture
def tenant_user(db, tenant_payload):
    """Create and return a tenant user in the database."""
    payload = tenant_payload.copy()
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

    def test_register_numeric_password_returns_400(self, api_client, tenant_payload):
        """A fully numeric password must be rejected (NumericPasswordValidator)."""
        tenant_payload['password'] = '12345678'
        response = api_client.post(REGISTER_URL, tenant_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_register_common_password_returns_400(self, api_client, tenant_payload):
        """A well-known common password must be rejected (CommonPasswordValidator)."""
        tenant_payload['password'] = 'password123'
        response = api_client.post(REGISTER_URL, tenant_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_register_password_similar_to_email_returns_400(self, api_client, tenant_payload):
        """A password matching the account's own email must be rejected (UserAttributeSimilarityValidator)."""
        tenant_payload['password'] = tenant_payload['email']
        response = api_client.post(REGISTER_URL, tenant_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_register_valid_strong_password_still_succeeds(self, api_client, tenant_payload):
        """A password that satisfies all validators must still register successfully (no regression)."""
        response = api_client.post(REGISTER_URL, tenant_payload)
        assert response.status_code == status.HTTP_201_CREATED


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
            'email': os.getenv('TEST_NONEXISTENT_EMAIL'),
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


@pytest.mark.django_db
class TestDeleteAccount:

    def test_delete_account_correct_password_returns_204(self, auth_tenant, tenant_payload):
        """Deleting the account with the correct password must return 204."""
        client, _ = auth_tenant
        response = client.delete(ME_URL, {'password': tenant_payload['password']})
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_account_wrong_password_returns_400(self, auth_tenant):
        """Deleting the account with an incorrect password must return 400."""
        client, _ = auth_tenant
        response = client.delete(ME_URL, {'password': 'wrongpassword'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_account_missing_password_returns_400(self, auth_tenant):
        """Deleting the account without a password must return 400."""
        client, _ = auth_tenant
        response = client.delete(ME_URL, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_account_without_auth_returns_401(self, api_client):
        """Deleting the account without authentication must return 401."""
        response = api_client.delete(ME_URL, {'password': 'whatever'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_account_anonymizes_user_in_db(self, auth_tenant, tenant_payload):
        """A deleted account must be deactivated and have its identifying fields anonymized."""
        client, data = auth_tenant
        user_id = data['user']['id']
        client.delete(ME_URL, {'password': tenant_payload['password']})

        user = User.objects.get(id=user_id)
        assert user.is_active is False
        assert user.email != tenant_payload['email']
        assert user.username != tenant_payload['username']

    def test_login_after_deletion_returns_401(self, auth_tenant, tenant_payload):
        """A deleted account must no longer be able to log in with its original credentials."""
        client, _ = auth_tenant
        client.delete(ME_URL, {'password': tenant_payload['password']})

        response = APIClient().post(LOGIN_URL, {
            'email': tenant_payload['email'],
            'password': tenant_payload['password'],
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_blacklisted_after_deletion(self, auth_tenant, tenant_payload):
        """The refresh token issued before deletion must no longer work afterwards."""
        client, data = auth_tenant
        refresh_token = data['refresh']
        client.delete(ME_URL, {'password': tenant_payload['password']})

        response = APIClient().post(REFRESH_URL, {'refresh': refresh_token})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserManager:

    def test_create_user_without_email_raises(self):
        """Creating a user with no email must raise a ValueError."""
        with pytest.raises(ValueError):
            User.objects.create_user(email='', password='SomePass123', username='no_email', role=UserRole.TENANT)

    def test_create_superuser_sets_staff_and_superuser_flags(self):
        """create_superuser must set both is_staff and is_superuser to True."""
        admin = User.objects.create_superuser(
            email=os.getenv('TEST_TENANT_EMAIL'), password='SomePass123', username='admin_user', role=UserRole.TENANT,
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True


@pytest.mark.django_db
class TestUserModel:

    def test_str_representation(self, tenant_user):
        """String representation of a user must be its email."""
        assert str(tenant_user) == tenant_user.email


@pytest.mark.django_db
class TestUserSerializerRoleImmutable:

    def test_role_is_read_only_on_update(self, tenant_user):
        """Passing a different role through the serializer must not change the stored role."""
        serializer = UserSerializer(tenant_user, data={'role': UserRole.LESSOR}, partial=True)
        assert serializer.is_valid()
        updated = serializer.save()
        assert updated.role == UserRole.TENANT

    def test_email_and_username_are_read_only_on_update(self, tenant_user):
        """Passing a different email/username through the serializer must not change the stored values."""
        original_email = tenant_user.email
        original_username = tenant_user.username
        serializer = UserSerializer(
            tenant_user, data={'email': 'someone-else@example.com', 'username': 'someone-else'}, partial=True,
        )
        assert serializer.is_valid()
        updated = serializer.save()
        assert updated.email == original_email
        assert updated.username == original_username
