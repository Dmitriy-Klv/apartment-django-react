from django.contrib.auth import authenticate
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView as BaseTokenRefreshView

from apps.common.serializers import ErrorResponseSerializer
from apps.users.serializers.user import DeleteAccountSerializer, LogoutSerializer, RegisterSerializer, UserSerializer
from apps.users.services.user import UserService

TokenPairResponseSerializer = inline_serializer(
    name='TokenPairResponse',
    fields={
        'user': UserSerializer(),
        'access': serializers.CharField(),
        'refresh': serializers.CharField(),
    },
)

LoginRequestSerializer = inline_serializer(
    name='LoginRequest',
    fields={
        'email': serializers.EmailField(),
        'password': serializers.CharField(write_only=True),
    },
)


class RegisterView(APIView):
    """Register a new user and return JWT tokens."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth'],
        summary='Register a new user',
        description='Create an account with the given role (tenant or lessor) and return an access/refresh token pair.',
        request=RegisterSerializer,
        responses={
            201: TokenPairResponseSerializer,
            400: OpenApiResponse(description='Validation error: field-specific messages (e.g. email or username already taken).'),
        },
    )
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

    @extend_schema(
        tags=['Auth'],
        summary='Log in with email and password',
        description='Authenticate with email/password and return an access/refresh token pair.',
        request=LoginRequestSerializer,
        responses={
            200: TokenPairResponseSerializer,
            400: OpenApiResponse(response=ErrorResponseSerializer, description='Email and password are required.'),
            401: OpenApiResponse(response=ErrorResponseSerializer, description='Invalid credentials.'),
        },
    )
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

    @extend_schema(
        tags=['Auth'],
        summary='Log out',
        description='Blacklist the given refresh token, invalidating it for future use.',
        request=LogoutSerializer,
        responses={
            204: None,
            400: OpenApiResponse(response=ErrorResponseSerializer, description='Token is invalid, malformed, or already blacklisted.'),
        },
    )
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
    """Return or delete the authenticated user's profile."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Auth'],
        summary='Get the current user',
        description="Return the authenticated user's own profile.",
        responses={200: UserSerializer},
    )
    def get(self, request):
        """Return current user's data."""
        return Response(UserSerializer(request.user).data)

    @extend_schema(
        tags=['Auth'],
        summary='Delete the current account (GDPR Art. 17)',
        description='Verify the given password, then anonymize the account and blacklist all of its tokens.',
        request=DeleteAccountSerializer,
        responses={
            204: None,
            400: OpenApiResponse(description='Incorrect password.'),
        },
    )
    def delete(self, request):
        """Verify the password, then anonymize the account and blacklist its tokens."""
        serializer = DeleteAccountSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        UserService.delete_account(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Auth'], summary='Refresh the access token')
class TokenRefreshView(BaseTokenRefreshView):
    """Refresh the access token using a valid refresh token."""
