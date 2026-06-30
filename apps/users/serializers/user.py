from rest_framework import serializers

from apps.users.models import User, UserRole


class RegisterSerializer(serializers.Serializer):
    """Validate incoming data for user registration."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    role = serializers.ChoiceField(choices=UserRole.choices)

    def validate_email(self, value):
        """Ensure the email address is not already registered."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value


class UserSerializer(serializers.ModelSerializer):
    """Serialize user data for read-only responses."""

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'created_at']


class LogoutSerializer(serializers.Serializer):
    """Accept a refresh token for logout."""

    refresh = serializers.CharField()
