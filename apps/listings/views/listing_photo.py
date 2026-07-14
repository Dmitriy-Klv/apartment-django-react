from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.listings.models import Listing, ListingPhoto
from apps.listings.serializers.listing_photo import ListingPhotoSerializer, ListingPhotoUploadSerializer
from apps.listings.services.listing_photo import ListingPhotoService
from apps.users.permissions import IsLessor


class ListingPhotoListCreateView(APIView):
    """Upload a new photo for a listing owned by the authenticated lessor."""

    permission_classes = [IsAuthenticated, IsLessor]

    def post(self, request, pk):
        """Validate and attach a new photo, enforcing the per-listing photo limit."""
        listing = get_object_or_404(Listing, pk=pk, deleted_at__isnull=True)
        if listing.owner != request.user:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ListingPhotoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        photo = ListingPhotoService.add_photo(listing, serializer.validated_data['image'])
        return Response(
            ListingPhotoSerializer(photo, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class ListingPhotoDetailView(APIView):
    """Set a listing photo as the cover photo, or delete it."""

    permission_classes = [IsAuthenticated, IsLessor]

    def patch(self, request, pk, photo_id):
        """Mark this photo as the listing's cover photo."""
        photo = get_object_or_404(ListingPhoto, pk=photo_id, listing_id=pk, listing__deleted_at__isnull=True)
        if photo.listing.owner != request.user:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

        photo = ListingPhotoService.set_primary(photo)
        return Response(ListingPhotoSerializer(photo, context={'request': request}).data)

    def delete(self, request, pk, photo_id):
        """Remove the photo from the listing."""
        photo = get_object_or_404(ListingPhoto, pk=photo_id, listing_id=pk, listing__deleted_at__isnull=True)
        if photo.listing.owner != request.user:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

        ListingPhotoService.delete_photo(photo)
        return Response(status=status.HTTP_204_NO_CONTENT)
