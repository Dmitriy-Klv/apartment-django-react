from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.serializers import ErrorResponseSerializer
from apps.history.services.search_history import SearchHistoryService
from apps.history.services.view_history import ViewHistoryService
from apps.listings.filters.listing import ListingFilter
from apps.listings.models import Listing
from apps.listings.serializers.listing import ListingCreateSerializer, ListingSerializer
from apps.listings.services.listing import ListingService
from apps.users.permissions import IsLessor


class IsListingOwner(BasePermission):
    """Allow write access only to the owner of the listing."""

    def has_object_permission(self, request, view, obj):
        """Return True if the requesting user owns the listing."""
        return obj.owner == request.user


@extend_schema_view(
    list=extend_schema(
        tags=['Listings'],
        summary='List active listings',
        description='Public catalog of active listings. Supports filtering (price, rooms, city, district, property type), free-text search, and ordering.',
    ),
    create=extend_schema(
        tags=['Listings'],
        summary='Create a listing (lessor only)',
        request=ListingCreateSerializer,
        responses={
            201: ListingSerializer,
            400: OpenApiResponse(description='Validation error: field-specific messages.'),
            403: OpenApiResponse(response=ErrorResponseSerializer, description='Only lessors may create listings.'),
        },
    ),
)
class ListingListCreateView(generics.ListCreateAPIView):
    """Public listing of active objects; creation restricted to Lessor role."""

    filterset_class = ListingFilter
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'views_count', 'reviews_count', 'average_rating']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return active, non-deleted listings."""
        return Listing.objects.filter(is_active=True, deleted_at__isnull=True).select_related('owner').prefetch_related('photos')

    def get_serializer_class(self):
        """Use create serializer for POST, full serializer for GET."""
        if self.request.method == 'POST':
            return ListingCreateSerializer
        return ListingSerializer

    def get_permissions(self):
        """POST requires Lessor; GET is public."""
        if self.request.method == 'POST':
            return [IsLessor()]
        return [AllowAny()]

    def list(self, request, *args, **kwargs):
        """List listings and save search keyword to history for authenticated users."""
        response = super().list(request, *args, **kwargs)
        keyword = request.query_params.get('search', '').strip()
        if keyword and request.user.is_authenticated:
            SearchHistoryService.record_search(user=request.user, keyword=keyword)
        return response

    def create(self, request, *args, **kwargs):
        """Create a new listing owned by the authenticated lessor."""
        serializer = ListingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        listing = ListingService.create_listing(
            owner=request.user,
            validated_data=serializer.validated_data,
        )
        return Response(
            ListingSerializer(listing, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    retrieve=extend_schema(
        tags=['Listings'],
        summary='Get listing details',
        description='Publicly retrieve any non-deleted listing; also records a view in the history.',
        responses={
            200: ListingSerializer,
            404: OpenApiResponse(response=ErrorResponseSerializer, description='Listing not found.'),
        },
    ),
    update=extend_schema(
        tags=['Listings'],
        summary='Replace a listing (owner only)',
        request=ListingCreateSerializer,
        responses={
            200: ListingSerializer,
            400: OpenApiResponse(description='Validation error: field-specific messages.'),
            403: OpenApiResponse(response=ErrorResponseSerializer, description='Only the owning lessor may update this listing.'),
            404: OpenApiResponse(response=ErrorResponseSerializer, description='Listing not found.'),
        },
    ),
    partial_update=extend_schema(
        tags=['Listings'],
        summary='Update a listing (owner only)',
        request=ListingCreateSerializer,
        responses={
            200: ListingSerializer,
            400: OpenApiResponse(description='Validation error: field-specific messages.'),
            403: OpenApiResponse(response=ErrorResponseSerializer, description='Only the owning lessor may update this listing.'),
            404: OpenApiResponse(response=ErrorResponseSerializer, description='Listing not found.'),
        },
    ),
    destroy=extend_schema(
        tags=['Listings'],
        summary='Soft-delete a listing (owner only)',
        responses={
            204: None,
            403: OpenApiResponse(response=ErrorResponseSerializer, description='Only the owning lessor may delete this listing.'),
            404: OpenApiResponse(response=ErrorResponseSerializer, description='Listing not found.'),
        },
    ),
)
class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve any non-deleted listing publicly; write requires ownership."""

    def get_queryset(self):
        """Return non-deleted listings for detail, update, and delete."""
        return Listing.objects.filter(deleted_at__isnull=True).select_related('owner').prefetch_related('photos')

    def get_serializer_class(self):
        """Use create serializer for write operations, full serializer for read."""
        if self.request.method in ('PUT', 'PATCH'):
            return ListingCreateSerializer
        return ListingSerializer

    def get_permissions(self):
        """Write operations require authentication, Lessor role, and ownership."""
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAuthenticated(), IsLessor(), IsListingOwner()]
        return [AllowAny()]

    def retrieve(self, request, *args, **kwargs):
        """Return listing details and record the view in history."""
        listing = self.get_object()
        user = request.user if request.user.is_authenticated else None
        ViewHistoryService.record_view(listing=listing, user=user)
        serializer = self.get_serializer(listing)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Update listing fields via the service layer."""
        partial = kwargs.pop('partial', False)
        listing = self.get_object()
        serializer = ListingCreateSerializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        listing = ListingService.update_listing(listing, serializer.validated_data)
        return Response(ListingSerializer(listing, context={'request': request}).data)

    def destroy(self, request, *args, **kwargs):
        """Soft-delete the listing instead of removing it from the database."""
        listing = self.get_object()
        ListingService.delete_listing(listing)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(
        tags=['Listings'],
        summary="List the current lessor's listings",
        description='Return all non-deleted listings (active and inactive) owned by the authenticated lessor.',
    ),
)
class MyListingsView(generics.ListAPIView):
    """Return all non-deleted listings belonging to the authenticated lessor."""

    serializer_class = ListingSerializer
    permission_classes = [IsLessor]

    def get_queryset(self):
        """Return only listings owned by the current user."""
        if getattr(self, 'swagger_fake_view', False):
            return Listing.objects.none()
        return Listing.objects.filter(
            owner=self.request.user, deleted_at__isnull=True
        ).select_related('owner').prefetch_related('photos')


class ListingToggleView(APIView):
    """Toggle the is_active status of a listing owned by the lessor."""

    permission_classes = [IsAuthenticated, IsLessor]

    @extend_schema(
        tags=['Listings'],
        summary='Toggle a listing active/inactive (owner only)',
        request=None,
        responses={
            200: ListingSerializer,
            403: OpenApiResponse(response=ErrorResponseSerializer, description='Only the owning lessor may toggle this listing.'),
            404: OpenApiResponse(response=ErrorResponseSerializer, description='Listing not found.'),
        },
    )
    def patch(self, request, pk):
        """Flip is_active and return the updated listing."""
        listing = get_object_or_404(Listing, pk=pk, deleted_at__isnull=True)
        if listing.owner != request.user:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        listing = ListingService.toggle_active(listing)
        return Response(ListingSerializer(listing, context={'request': request}).data)
