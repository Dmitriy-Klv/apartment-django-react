from apps.users.models import User


class UserService:
    @staticmethod
    def create_user(email: str, password: str, first_name: str, last_name: str, role: str) -> User:
        """Create and return a new user with a hashed password."""
        return User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
