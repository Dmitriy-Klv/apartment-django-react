from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView

from apps.users.serializers.user import LogoutSerializer, RegisterSerializer, UserSerializer
from apps.users.services.user import UserService


class RegisterView(APIView):
    """Register a new user and return JWT tokens."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validate registration data, create user, and return tokens."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = UserService.create_user(
            email=data['email'],
            password=data['password'],
            username=data['username'],
            role=data['role'],
        )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Authenticate user with email/password and return JWT tokens."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validate credentials and issue tokens on success."""
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'detail': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response(
                {'detail': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class LogoutView(APIView):
    """Blacklist the refresh token to invalidate the session."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Accept a refresh token and add it to the blacklist."""
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data['refresh'])
            token.blacklist()
        except TokenError:
            return Response(
                {'detail': 'Token is invalid or already blacklisted.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    """Return the authenticated user's profile."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return current user's data."""
        return Response(UserSerializer(request.user).data)


class TokenRefreshView(BaseTokenRefreshView):
    """Refresh the access token using a valid refresh token."""
