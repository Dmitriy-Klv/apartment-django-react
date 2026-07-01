from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.bookings.models import Booking, BookingStatus
from apps.reviews.models import Review


class ReviewService:

    @staticmethod
    def create_review(author, booking: Booking, rating: int, comment: str) -> Review:
        """Create a review for a checked-in booking owned by the author."""
        if booking.tenant_id != author.id:
            raise PermissionDenied('You can only review your own booking.')
        if booking.status != BookingStatus.CHECKED_IN:
            raise ValidationError('You can only review a booking after check-in.')
        if Review.objects.filter(booking=booking).exists():
            raise ValidationError('This booking has already been reviewed.')

        return Review.objects.create(
            listing=booking.listing,
            author=author,
            booking=booking,
            rating=rating,
            comment=comment,
        )
