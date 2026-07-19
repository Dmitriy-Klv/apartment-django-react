from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.listings.models import Listing
from apps.listings.serializers.listing_photo import ListingPhotoSerializer


class ListingSerializer(serializers.ModelSerializer):
    """Full listing representation for read operations."""

    owner_username = serializers.CharField(source='owner.username', read_only=True, help_text="The listing owner's public display name.")
    photos = ListingPhotoSerializer(many=True, read_only=True, help_text='All photos uploaded for this listing.')
    cover_image = serializers.SerializerMethodField(help_text='Absolute URL of the primary photo, or the first uploaded photo if none is marked primary. Null if no photos exist.')

    class Meta:
        model = Listing
        fields = [
            'id', 'owner', 'owner_username', 'title', 'description',
            'city', 'district', 'postal_code', 'price', 'rooms',
            'property_type', 'photos', 'cover_image', 'is_active', 'views_count',
            'average_rating', 'reviews_count', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'owner', 'owner_username', 'photos', 'cover_image', 'views_count',
            'average_rating', 'reviews_count', 'created_at', 'updated_at',
        ]

    @extend_schema_field(serializers.URLField(allow_null=True))
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
