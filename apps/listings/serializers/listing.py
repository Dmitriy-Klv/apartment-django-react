from rest_framework import serializers

from apps.listings.models import Listing
from apps.listings.serializers.listing_photo import ListingPhotoSerializer


class ListingSerializer(serializers.ModelSerializer):
    """Full listing representation for read operations."""

    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    photos = ListingPhotoSerializer(many=True, read_only=True)
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            'id', 'owner', 'owner_email', 'title', 'description',
            'city', 'district', 'postal_code', 'price', 'rooms',
            'property_type', 'photos', 'cover_image', 'is_active', 'views_count',
            'average_rating', 'reviews_count', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'owner', 'owner_email', 'photos', 'cover_image', 'views_count',
            'average_rating', 'reviews_count', 'created_at', 'updated_at',
        ]

    def get_cover_image(self, obj):
        """Return the URL of the primary photo, falling back to the first uploaded photo."""
        photo = next((p for p in obj.photos.all() if p.is_primary), None) or next(iter(obj.photos.all()), None)
        if not photo:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(photo.image.url) if request else photo.image.url


class ListingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating a listing."""

    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'city', 'district',
            'postal_code', 'price', 'rooms', 'property_type', 'is_active',
        ]
