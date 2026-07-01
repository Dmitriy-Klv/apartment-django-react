from django.contrib import admin

from apps.bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin configuration for Booking model."""

    list_display = ['listing', 'tenant', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['listing__title', 'tenant__email']
    readonly_fields = ['created_at', 'updated_at']
