from rest_framework import serializers

from apps.bookings.models import Booking
from apps.reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Full review representation for read operations."""

    author_username = serializers.CharField(source='author.username', read_only=True)
    listing_title = serializers.CharField(source='listing.title', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'listing', 'listing_title', 'author', 'author_username',
            'booking', 'rating', 'comment', 'created_at',
        ]
        read_only_fields = fields


class ReviewCreateSerializer(serializers.Serializer):
    """Validate incoming data for creating a review."""

    booking = serializers.PrimaryKeyRelatedField(queryset=Booking.objects.all())
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField()
