from datetime import date, timedelta

from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.bookings.models import Booking, BookingStatus
from apps.listings.models import Listing

ACTIVE_STATUSES = [BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN]
MIN_CANCEL_LEAD_DAYS = 2


class BookingService:

    @staticmethod
    def create_booking(tenant, listing: Listing, start_date: date, end_date: date) -> Booking:
        """Create a booking after checking ownership and date overlap rules."""
        if listing.owner_id == tenant.id:
            raise ValidationError('You cannot book your own listing.')

        overlapping = Booking.objects.filter(
            listing=listing,
            status__in=ACTIVE_STATUSES,
            start_date__lt=end_date,
            end_date__gt=start_date,
        ).exists()
        if overlapping:
            raise ValidationError('Listing is already booked for the selected dates.')

        return Booking.objects.create(
            listing=listing,
            tenant=tenant,
            start_date=start_date,
            end_date=end_date,
        )

    @staticmethod
    def cancel_booking(booking: Booking, user) -> Booking:
        """Cancel a pending booking; only the tenant, at least 2 days before start."""
        if booking.tenant_id != user.id:
            raise PermissionDenied('Only the tenant can cancel this booking.')
        if booking.status != BookingStatus.PENDING:
            raise ValidationError('Only a pending booking can be canceled.')
        if date.today() >= booking.start_date - timedelta(days=MIN_CANCEL_LEAD_DAYS):
            raise ValidationError(f'Booking can only be canceled at least {MIN_CANCEL_LEAD_DAYS} days before start.')

        booking.status = BookingStatus.CANCELED
        booking.save(update_fields=['status', 'updated_at'])
        return booking

    @staticmethod
    def confirm_booking(booking: Booking, user) -> Booking:
        """Confirm a pending booking; only the listing owner."""
        BookingService._require_lessor(booking, user)
        if booking.status != BookingStatus.PENDING:
            raise ValidationError('Only a pending booking can be confirmed.')

        booking.status = BookingStatus.CONFIRMED
        booking.save(update_fields=['status', 'updated_at'])
        return booking

    @staticmethod
    def reject_booking(booking: Booking, user) -> Booking:
        """Reject a pending booking; only the listing owner."""
        BookingService._require_lessor(booking, user)
        if booking.status != BookingStatus.PENDING:
            raise ValidationError('Only a pending booking can be rejected.')

        booking.status = BookingStatus.REJECTED
        booking.save(update_fields=['status', 'updated_at'])
        return booking

    @staticmethod
    def check_in_booking(booking: Booking, user) -> Booking:
        """Check in a confirmed booking; only the listing owner."""
        BookingService._require_lessor(booking, user)
        if booking.status != BookingStatus.CONFIRMED:
            raise ValidationError('Only a confirmed booking can be checked in.')

        booking.status = BookingStatus.CHECKED_IN
        booking.save(update_fields=['status', 'updated_at'])
        return booking

    @staticmethod
    def _require_lessor(booking: Booking, user) -> None:
        """Raise if the user is not the owner of the booked listing."""
        if booking.listing.owner_id != user.id:
            raise PermissionDenied('Only the listing owner can perform this action.')
