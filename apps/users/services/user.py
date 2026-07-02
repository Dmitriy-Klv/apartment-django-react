from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from apps.users.models import User


class UserService:
    @staticmethod
    def create_user(email: str, password: str, username: str, role: str) -> User:
        """Create and return a new user with a hashed password."""
        return User.objects.create_user(
            email=email,
            password=password,
            username=username,
            role=role,
        )

    @staticmethod
    def delete_account(user: User) -> None:
        """Anonymize the account, deactivate it, and blacklist all outstanding tokens."""
        user.email = f'deleted-{user.id}@deleted.invalid'
        user.username = f'deleted_user_{user.id}'
        user.is_active = False
        user.save(update_fields=['email', 'username', 'is_active', 'updated_at'])

        for outstanding_token in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=outstanding_token)
