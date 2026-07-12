from django.urls import path

from apps.bookings.views.booking import (
    BookingDetailView,
    BookingListCreateView,
    BookingStatusUpdateView,
    LessorBookingsView,
    ListingBookedDatesView,
)

urlpatterns = [
    path('', BookingListCreateView.as_view(), name='booking-list'),
    path('lessor/', LessorBookingsView.as_view(), name='booking-lessor'),
    path('listings/<int:listing_id>/booked-dates/', ListingBookedDatesView.as_view(), name='booking-listing-dates'),
    path('<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('<int:pk>/status/', BookingStatusUpdateView.as_view(), name='booking-status'),
]
