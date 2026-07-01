from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.models import Booking, BookingStatus
from apps.bookings.serializers.booking import BookingCreateSerializer, BookingSerializer, BookingStatusSerializer
from apps.bookings.services.booking import BookingService
from apps.users.permissions import IsLessor, IsTenant

STATUS_ACTIONS = {
    BookingStatus.CONFIRMED: BookingService.confirm_booking,
    BookingStatus.REJECTED: BookingService.reject_booking,
    BookingStatus.CANCELED: BookingService.cancel_booking,
    BookingStatus.CHECKED_IN: BookingService.check_in_booking,
}


class IsBookingParticipant(BasePermission):
    """Allow access only to the tenant or the listing owner of the booking."""

    def has_object_permission(self, request, view, obj):
        """Return True if the requesting user is the tenant or the listing owner."""
        return obj.tenant_id == request.user.id or obj.listing.owner_id == request.user.id


class BookingListCreateView(generics.ListCreateAPIView):
    """List the authenticated tenant's bookings and create new ones."""

    serializer_class = BookingSerializer

    def get_queryset(self):
        """Return bookings made by the authenticated tenant."""
        return Booking.objects.filter(tenant=self.request.user).select_related('listing', 'tenant')

    def get_permissions(self):
        """Creation requires the tenant role; listing requires authentication."""
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsTenant()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """Create a booking for the authenticated tenant via the service layer."""
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = BookingService.create_booking(
            tenant=request.user,
            listing=serializer.validated_data['listing'],
            start_date=serializer.validated_data['start_date'],
            end_date=serializer.validated_data['end_date'],
        )
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)


class BookingDetailView(generics.RetrieveAPIView):
    """Retrieve a single booking visible to its tenant or the listing owner."""

    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsBookingParticipant]

    def get_queryset(self):
        """Return all bookings; object-level permission restricts access."""
        return Booking.objects.select_related('listing', 'tenant')


class BookingStatusUpdateView(APIView):
    """Transition a booking to a new status via the service layer."""

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        """Validate the requested status and delegate the transition to the service."""
        booking = get_object_or_404(Booking.objects.select_related('listing', 'tenant'), pk=pk)
        serializer = BookingStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action = STATUS_ACTIONS[serializer.validated_data['status']]
        booking = action(booking, request.user)
        return Response(BookingSerializer(booking).data)


class LessorBookingsView(generics.ListAPIView):
    """List all bookings made on the authenticated lessor's listings."""

    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsLessor]

    def get_queryset(self):
        """Return bookings for listings owned by the current lessor."""
        return Booking.objects.filter(listing__owner=self.request.user).select_related('listing', 'tenant')
