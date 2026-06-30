from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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


class ListingListCreateView(generics.ListCreateAPIView):
    """Public listing of active objects; creation restricted to Lessor role."""

    filterset_class = ListingFilter
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'views_count', 'reviews_count', 'average_rating']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return active, non-deleted listings."""
        return Listing.objects.filter(is_active=True, is_deleted=False).select_related('owner')

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

    def create(self, request, *args, **kwargs):
        """Create a new listing owned by the authenticated lessor."""
        serializer = ListingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        listing = ListingService.create_listing(
            owner=request.user,
            validated_data=serializer.validated_data,
        )
        return Response(ListingSerializer(listing).data, status=status.HTTP_201_CREATED)


class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve any non-deleted listing publicly; write requires ownership."""

    def get_queryset(self):
        """Return non-deleted listings for detail, update, and delete."""
        return Listing.objects.filter(is_deleted=False).select_related('owner')

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

    def update(self, request, *args, **kwargs):
        """Update listing fields via the service layer."""
        partial = kwargs.pop('partial', False)
        listing = self.get_object()
        serializer = ListingCreateSerializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        listing = ListingService.update_listing(listing, serializer.validated_data)
        return Response(ListingSerializer(listing).data)

    def destroy(self, request, *args, **kwargs):
        """Soft-delete the listing instead of removing it from the database."""
        listing = self.get_object()
        ListingService.delete_listing(listing)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyListingsView(generics.ListAPIView):
    """Return all non-deleted listings belonging to the authenticated lessor."""

    serializer_class = ListingSerializer
    permission_classes = [IsLessor]

    def get_queryset(self):
        """Return only listings owned by the current user."""
        return Listing.objects.filter(
            owner=self.request.user, is_deleted=False
        ).select_related('owner')


class ListingToggleView(APIView):
    """Toggle the is_active status of a listing owned by the lessor."""

    permission_classes = [IsAuthenticated, IsLessor]

    def patch(self, request, pk):
        """Flip is_active and return the updated listing."""
        listing = get_object_or_404(Listing, pk=pk, is_deleted=False)
        if listing.owner != request.user:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        listing = ListingService.toggle_active(listing)
        return Response(ListingSerializer(listing).data)
