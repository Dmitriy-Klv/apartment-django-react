from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.serializers import ErrorResponseSerializer
from apps.listings.models import Listing, ListingPhoto
from apps.listings.serializers.listing_photo import ListingPhotoSerializer, ListingPhotoUploadSerializer
from apps.listings.services.listing_photo import ListingPhotoService
from apps.users.permissions import IsLessor


class ListingPhotoListCreateView(APIView):
    """Upload a new photo for a listing owned by the authenticated lessor."""

    permission_classes = [IsAuthenticated, IsLessor]

    @extend_schema(
        tags=['Listing Photos'],
        summary='Upload a listing photo (owner only)',
        description='Attach a new photo to the listing. A listing may hold at most 5 photos.',
        request=ListingPhotoUploadSerializer,
        responses={
            201: ListingPhotoSerializer,
            400: OpenApiResponse(description='Validation error: image too large, wrong format, or photo limit reached.'),
            403: OpenApiResponse(response=ErrorResponseSerializer, description='Only the owning lessor may upload photos.'),
            404: OpenApiResponse(response=ErrorResponseSerializer, description='Listing not found.'),
        },
    )
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

    @extend_schema(
        tags=['Listing Photos'],
        summary='Set the cover photo (owner only)',
        request=None,
        responses={
            200: ListingPhotoSerializer,
            403: OpenApiResponse(response=ErrorResponseSerializer, description='Only the owning lessor may change the cover photo.'),
            404: OpenApiResponse(response=ErrorResponseSerializer, description='Listing or photo not found.'),
        },
    )
    def patch(self, request, pk, photo_id):
        """Mark this photo as the listing's cover photo."""
        photo = get_object_or_404(ListingPhoto, pk=photo_id, listing_id=pk, listing__deleted_at__isnull=True)
        if photo.listing.owner != request.user:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

        photo = ListingPhotoService.set_primary(photo)
        return Response(ListingPhotoSerializer(photo, context={'request': request}).data)

    @extend_schema(
        tags=['Listing Photos'],
        summary='Delete a listing photo (owner only)',
        responses={
            204: None,
            403: OpenApiResponse(response=ErrorResponseSerializer, description='Only the owning lessor may delete this photo.'),
            404: OpenApiResponse(response=ErrorResponseSerializer, description='Listing or photo not found.'),
        },
    )
    def delete(self, request, pk, photo_id):
        """Remove the photo from the listing."""
        photo = get_object_or_404(ListingPhoto, pk=photo_id, listing_id=pk, listing__deleted_at__isnull=True)
        if photo.listing.owner != request.user:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

        ListingPhotoService.delete_photo(photo)
        return Response(status=status.HTTP_204_NO_CONTENT)
