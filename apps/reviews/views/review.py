from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.common.serializers import ErrorResponseSerializer
from apps.reviews.models import Review
from apps.reviews.serializers.review import ReviewCreateSerializer, ReviewSerializer
from apps.reviews.services.review import ReviewService
from apps.users.permissions import IsTenant


@extend_schema_view(
    create=extend_schema(
        tags=['Reviews'],
        summary='Create a review (tenant only)',
        description='Leave a rating and comment for a booking that has been checked in.',
        request=ReviewCreateSerializer,
        responses={
            201: ReviewSerializer,
            400: OpenApiResponse(description='Validation error: booking not checked in, already reviewed, or invalid rating.'),
            403: OpenApiResponse(response=ErrorResponseSerializer, description='Only tenants may leave reviews.'),
        },
    ),
)
class ReviewCreateView(generics.CreateAPIView):
    """Create a review for a checked-in booking; restricted to tenants."""

    serializer_class = ReviewCreateSerializer
    permission_classes = [IsAuthenticated, IsTenant]

    def create(self, request, *args, **kwargs):
        """Validate input and delegate review creation to the service layer."""
        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = ReviewService.create_review(
            author=request.user,
            booking=serializer.validated_data['booking'],
            rating=serializer.validated_data['rating'],
            comment=serializer.validated_data['comment'],
        )
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    retrieve=extend_schema(
        tags=['Reviews'],
        summary='Get review details',
        description='Publicly retrieve a single review.',
        responses={
            200: ReviewSerializer,
            404: OpenApiResponse(response=ErrorResponseSerializer, description='Review not found.'),
        },
    ),
)
class ReviewDetailView(generics.RetrieveAPIView):
    """Retrieve a single review; publicly visible."""

    queryset = Review.objects.select_related('listing', 'author')
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    list=extend_schema(
        tags=['Reviews'],
        summary='List reviews for a listing',
        description='Publicly list all reviews for a given listing.',
    ),
)
class ListingReviewsView(generics.ListAPIView):
    """List all reviews for a given listing; publicly visible."""

    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Return reviews belonging to the listing identified in the URL."""
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()
        return Review.objects.filter(listing_id=self.kwargs['listing_id']).select_related('listing', 'author')
