from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.models import Booking, BookingStatus
from apps.bookings.serializers.booking import (
    BookingCreateSerializer,
    BookingDateRangeSerializer,
    BookingSerializer,
    BookingStatusSerializer,
)
from apps.bookings.services.booking import ACTIVE_STATUSES, BookingService
from apps.common.serializers import ErrorResponseSerializer
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


@extend_schema_view(
    list=extend_schema(
        tags=['Bookings'],
        summary="List the current tenant's bookings",
        description='Return all bookings made by the authenticated tenant.',
    ),
    create=extend_schema(
        tags=['Bookings'],
        summary='Create a booking (tenant only)',
        request=BookingCreateSerializer,
        responses={
            201: BookingSerializer,
            400: OpenApiResponse(description='Validation error: invalid dates or overlapping booking.'),
            403: OpenApiResponse(response=ErrorResponseSerializer, description='Only tenants may create bookings.'),
        },
    ),
)
class BookingListCreateView(generics.ListCreateAPIView):
    """List the authenticated tenant's bookings and create new ones."""

    serializer_class = BookingSerializer

    def get_queryset(self):
        """Return bookings made by the authenticated tenant."""
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()
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


@extend_schema_view(
    retrieve=extend_schema(
        tags=['Bookings'],
        summary='Get booking details',
        description='Retrieve a single booking; visible only to its tenant or the listing owner.',
        responses={
            200: BookingSerializer,
            403: OpenApiResponse(response=ErrorResponseSerializer, description='Not a participant of this booking.'),
            404: OpenApiResponse(response=ErrorResponseSerializer, description='Booking not found.'),
        },
    ),
)
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

    @extend_schema(
        tags=['Bookings'],
        summary='Change a booking status',
        description=(
            'Transition a booking to confirmed, rejected, canceled, or checked-in. '
            'Each transition is restricted to the appropriate participant (lessor confirms/rejects/checks in, tenant cancels).'
        ),
        request=BookingStatusSerializer,
        responses={
            200: BookingSerializer,
            400: OpenApiResponse(description='Validation error: invalid status or illegal transition.'),
            403: OpenApiResponse(response=ErrorResponseSerializer, description='Not permitted to perform this transition.'),
            404: OpenApiResponse(response=ErrorResponseSerializer, description='Booking not found.'),
        },
    )
    def patch(self, request, pk):
        """Validate the requested status and delegate the transition to the service."""
        booking = get_object_or_404(Booking.objects.select_related('listing', 'tenant'), pk=pk)
        serializer = BookingStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        status_value = serializer.validated_data['status']
        action = STATUS_ACTIONS[status_value]
        if status_value == BookingStatus.REJECTED:
            booking = action(
                booking,
                request.user,
                serializer.validated_data['rejection_reason'],
                serializer.validated_data.get('rejection_note', ''),
            )
        else:
            booking = action(booking, request.user)
        return Response(BookingSerializer(booking).data)


@extend_schema_view(
    list=extend_schema(
        tags=['Bookings'],
        summary='Get booked date ranges for a listing',
        description='Public, PII-free date ranges of active bookings for a listing, used to block dates in the UI calendar.',
    ),
)
class ListingBookedDatesView(generics.ListAPIView):
    """Public date ranges of active bookings for a listing, used to block dates in the UI."""

    serializer_class = BookingDateRangeSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        """Return active booking date ranges for the requested listing."""
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()
        return Booking.objects.filter(
            listing_id=self.kwargs['listing_id'],
            status__in=ACTIVE_STATUSES,
        ).only('start_date', 'end_date').order_by('start_date')


@extend_schema_view(
    list=extend_schema(
        tags=['Bookings'],
        summary="List bookings on the current lessor's listings",
        description="Return all bookings made on any listing owned by the authenticated lessor.",
    ),
)
class LessorBookingsView(generics.ListAPIView):
    """List all bookings made on the authenticated lessor's listings."""

    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsLessor]

    def get_queryset(self):
        """Return bookings for listings owned by the current lessor."""
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()
        return Booking.objects.filter(listing__owner=self.request.user).select_related('listing', 'tenant')
