from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class BookingStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    REJECTED = 'rejected', 'Rejected'
    CANCELED = 'canceled', 'Canceled'
    CHECKED_IN = 'checked_in', 'Checked In'


class RejectionReason(models.TextChoices):
    DATES_UNAVAILABLE = 'dates_unavailable', 'Dates no longer available'
    LISTING_UNAVAILABLE = 'listing_unavailable', 'Listing temporarily unavailable'
    TENANT_REQUIREMENTS_NOT_MET = 'tenant_requirements_not_met', "Tenant doesn't meet requirements"
    SUSPICIOUS_REQUEST = 'suspicious_request', 'Suspicious or invalid request'
    OTHER = 'other', 'Other'


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
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
    )
    rejection_reason = models.CharField(
        max_length=30,
        choices=RejectionReason.choices,
        null=True,
        blank=True,
    )
    rejection_note = models.CharField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bookings_booking'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_date__gt=models.F('start_date')),
                name='booking_end_date_after_start_date',
            ),
        ]

    def __str__(self):
        return f'{self.tenant} — {self.listing} ({self.start_date}/{self.end_date})'
