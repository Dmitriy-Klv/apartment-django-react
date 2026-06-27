from django.conf import settings
from django.db import models


class BookingStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    REJECTED = 'rejected', 'Rejected'
    CANCELED = 'canceled', 'Canceled'
    CHECKED_IN = 'checked_in', 'Checked In'


class Booking(models.Model):
    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bookings_booking'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.tenant} — {self.listing} ({self.start_date}/{self.end_date})'
