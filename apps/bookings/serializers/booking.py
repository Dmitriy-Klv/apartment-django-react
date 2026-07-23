from datetime import date

from rest_framework import serializers

from apps.bookings.models import Booking, BookingStatus, RejectionReason
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
    tenant_email = serializers.EmailField(source='tenant.email', read_only=True, help_text='Only visible to the tenant and the listing owner; never exposed on public endpoints.')

    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_title', 'tenant', 'tenant_email',
            'start_date', 'end_date', 'price_per_night', 'total_price',
            'status', 'rejection_reason', 'rejection_note', 'created_at', 'updated_at',
        ]
        read_only_fields = fields


class BookingCreateSerializer(serializers.Serializer):
    """Validate incoming data for creating a booking."""

    listing = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.filter(is_active=True, deleted_at__isnull=True),
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
    rejection_reason = serializers.ChoiceField(choices=RejectionReason.choices, required=False)
    rejection_note = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate(self, attrs):
        """Require a reason (and a note for 'other') only when rejecting a booking."""
        status_value = attrs.get('status')
        reason = attrs.get('rejection_reason')
        note = attrs.get('rejection_note', '')

        if status_value == BookingStatus.REJECTED:
            if not reason:
                raise serializers.ValidationError({'rejection_reason': 'A rejection reason is required.'})
            if reason == RejectionReason.OTHER and not note.strip():
                raise serializers.ValidationError({'rejection_note': 'Please specify a reason when selecting "Other".'})
        elif reason or note:
            raise serializers.ValidationError('rejection_reason/rejection_note only apply when rejecting a booking.')

        return attrs
