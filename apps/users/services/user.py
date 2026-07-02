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
