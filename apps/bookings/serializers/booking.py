from datetime import date

from rest_framework import serializers

from apps.bookings.models import Booking, BookingStatus
from apps.listings.models import Listing

UPDATABLE_STATUSES = [
    BookingStatus.CONFIRMED,
    BookingStatus.REJECTED,
    BookingStatus.CANCELED,
    BookingStatus.CHECKED_IN,
]


class BookingSerializer(serializers.ModelSerializer):
    """Full booking representation for read operations."""

    listing_title = serializers.CharField(source='listing.title', read_only=True)
    tenant_email = serializers.EmailField(source='tenant.email', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_title', 'tenant', 'tenant_email',
            'start_date', 'end_date', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class BookingCreateSerializer(serializers.Serializer):
    """Validate incoming data for creating a booking."""

    listing = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.filter(is_active=True, is_deleted=False),
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate_start_date(self, value):
        """Reject dates in the past."""
        if value < date.today():
            raise serializers.ValidationError('Start date cannot be in the past.')
        return value

    def validate(self, attrs):
        """Ensure start date precedes end date."""
        if attrs['start_date'] >= attrs['end_date']:
            raise serializers.ValidationError('End date must be after start date.')
        return attrs


class BookingDateRangeSerializer(serializers.ModelSerializer):
    """Public date range of a single active booking, used to block dates in the UI."""

    class Meta:
        model = Booking
        fields = ['start_date', 'end_date']


class BookingStatusSerializer(serializers.Serializer):
    """Validate a booking status transition request."""

    status = serializers.ChoiceField(choices=UPDATABLE_STATUSES)
