from rest_framework import serializers

from apps.listings.models import ListingPhoto

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_CONTENT_TYPES = ('image/jpeg', 'image/png', 'image/webp')


class ListingPhotoSerializer(serializers.ModelSerializer):
    """Full listing photo representation for read operations."""

    class Meta:
        model = ListingPhoto
        fields = ['id', 'image', 'is_primary', 'created_at']
        read_only_fields = ['id', 'is_primary', 'created_at']


class ListingPhotoUploadSerializer(serializers.Serializer):
    """Validate an incoming photo upload."""

    image = serializers.ImageField(help_text='JPEG, PNG, or WebP, up to 5 MB.')

    def validate_image(self, value):
        """Reject images that are too large or not an allowed format."""
        if value.size > MAX_IMAGE_SIZE_BYTES:
            raise serializers.ValidationError('Image must be smaller than 5 MB.')
        if value.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
            raise serializers.ValidationError('Image must be JPEG, PNG, or WebP.')
        return value
