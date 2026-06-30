from rest_framework import serializers

from apps.listings.models import Listing


class ListingSerializer(serializers.ModelSerializer):
    """Full listing representation for read operations."""

    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id', 'owner', 'owner_email', 'title', 'description',
            'city', 'district', 'postal_code', 'price', 'rooms',
            'property_type', 'is_active', 'views_count',
            'average_rating', 'reviews_count', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'owner', 'owner_email', 'views_count',
            'average_rating', 'reviews_count', 'created_at', 'updated_at',
        ]


class ListingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating a listing."""

    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'city', 'district',
            'postal_code', 'price', 'rooms', 'property_type', 'is_active',
        ]
