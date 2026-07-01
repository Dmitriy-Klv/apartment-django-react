import os
from datetime import date, timedelta

import pytest
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.bookings.models import Booking, BookingStatus
from apps.bookings.services.booking import BookingService
from apps.listings.models import Listing, PropertyType
from apps.users.models import User, UserRole

BOOKINGS_URL = '/api/v1/bookings/'
LESSOR_BOOKINGS_URL = '/api/v1/bookings/lessor/'


@pytest.fixture
def tenant_client_2(db):
    """Return (APIClient, user) for a second authenticated tenant."""
    user = User.objects.create_user(
        email=os.getenv('TEST_TENANT2_EMAIL'),
        password=os.getenv('TEST_USER_PASSWORD'),
        first_name='Second',
        last_name='Tenant',
        role=UserRole.TENANT,
    )
    client = APIClient()
    token = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(token.access_token)}')
    return client, user


@pytest.fixture
def listing(db, lessor_client):
    """Active listing owned by lessor_client's user."""
    _, owner = lessor_client
    return Listing.objects.create(
        owner=owner,
        title='Apartment in Berlin',
        description='Cozy 2-room apartment.',
        city='Berlin',
        district='Mitte',
        postal_code=os.getenv('TEST_LISTING_POSTAL_CODE', '00000'),
        price='1000.00',
        rooms=2,
        property_type=PropertyType.APARTMENT,
        is_active=True,
    )


def future_dates(start_offset=10, length=3):
    """Return (start_date, end_date) strings for a booking, offset from today."""
    start = date.today() + timedelta(days=start_offset)
    end = start + timedelta(days=length)
    return start.isoformat(), end.isoformat()


def results_of(response_data):
    """Return the list of results from a paginated or plain list response."""
    return response_data['results'] if isinstance(response_data, dict) else response_data


@pytest.mark.django_db
class TestBookingCreate:

    def test_tenant_creates_booking_201(self, tenant_client, listing):
        """Tenant must be able to book a listing on free dates."""
        client, _ = tenant_client
        start, end = future_dates()
        response = client.post(BOOKINGS_URL, {'listing': listing.id, 'start_date': start, 'end_date': end})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == BookingStatus.PENDING

    def test_lessor_cannot_create_403(self, lessor_client_2, listing):
        """Lessor role must not be able to create a booking."""
        client, _ = lessor_client_2
        start, end = future_dates()
        response = client.post(BOOKINGS_URL, {'listing': listing.id, 'start_date': start, 'end_date': end})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_anonymous_cannot_create_401(self, api_client, listing):
        """Unauthenticated request must be rejected."""
        start, end = future_dates()
        response = api_client.post(BOOKINGS_URL, {'listing': listing.id, 'start_date': start, 'end_date': end})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_start_date_in_past_400(self, tenant_client, listing):
        """Booking with a start date in the past must be rejected."""
        client, _ = tenant_client
        past = (date.today() - timedelta(days=1)).isoformat()
        end = date.today().isoformat()
        response = client.post(BOOKINGS_URL, {'listing': listing.id, 'start_date': past, 'end_date': end})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_start_after_end_400(self, tenant_client, listing):
        """Start date must be strictly before end date."""
        client, _ = tenant_client
        start, end = future_dates()
        response = client.post(BOOKINGS_URL, {'listing': listing.id, 'start_date': end, 'end_date': start})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_overlapping_dates_400(self, tenant_client, tenant_client_2, listing):
        """A second booking on overlapping dates must be rejected."""
        client, _ = tenant_client
        start, end = future_dates()
        client.post(BOOKINGS_URL, {'listing': listing.id, 'start_date': start, 'end_date': end})

        client2, _ = tenant_client_2
        response = client2.post(BOOKINGS_URL, {'listing': listing.id, 'start_date': start, 'end_date': end})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_non_overlapping_dates_201(self, tenant_client, tenant_client_2, listing):
        """A second booking on free dates must be accepted."""
        client, _ = tenant_client
        start1, end1 = future_dates(start_offset=1, length=2)
        client.post(BOOKINGS_URL, {'listing': listing.id, 'start_date': start1, 'end_date': end1})

        client2, _ = tenant_client_2
        start2, end2 = future_dates(start_offset=10, length=2)
        response = client2.post(BOOKINGS_URL, {'listing': listing.id, 'start_date': start2, 'end_date': end2})
        assert response.status_code == status.HTTP_201_CREATED

    def test_cannot_book_own_listing(self, db, lessor_client, listing):
        """A user cannot create a booking on a listing they own themselves."""
        _, owner = lessor_client
        start, end = future_dates()
        with pytest.raises(ValidationError):
            BookingService.create_booking(
                tenant=owner,
                listing=listing,
                start_date=date.fromisoformat(start),
                end_date=date.fromisoformat(end),
            )


@pytest.mark.django_db
class TestBookingList:

    def test_tenant_sees_only_own_bookings(self, tenant_client, tenant_client_2, listing):
        """Tenant's booking list must not include other tenants' bookings."""
        client, user = tenant_client
        start, end = future_dates()
        client.post(BOOKINGS_URL, {'listing': listing.id, 'start_date': start, 'end_date': end})

        client2, _ = tenant_client_2
        response = client2.get(BOOKINGS_URL)
        assert len(results_of(response.data)) == 0

    def test_lessor_sees_bookings_for_own_listings(self, tenant_client, lessor_client, listing):
        """Lessor bookings endpoint must return bookings made on their listings."""
        client, _ = tenant_client
        start, end = future_dates()
        client.post(BOOKINGS_URL, {'listing': listing.id, 'start_date': start, 'end_date': end})

        lessor, _ = lessor_client
        response = lessor.get(LESSOR_BOOKINGS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(results_of(response.data)) == 1

    def test_other_lessor_sees_no_bookings(self, tenant_client, lessor_client_2, listing):
        """A lessor with no listings must see an empty booking list."""
        client, _ = tenant_client
        start, end = future_dates()
        client.post(BOOKINGS_URL, {'listing': listing.id, 'start_date': start, 'end_date': end})

        other_lessor, _ = lessor_client_2
        response = other_lessor.get(LESSOR_BOOKINGS_URL)
        assert len(results_of(response.data)) == 0


@pytest.mark.django_db
class TestBookingDetail:

    def test_tenant_can_view_own_booking(self, tenant_client, listing):
        """The tenant who made the booking must be able to view it."""
        client, _ = tenant_client
        start, end = future_dates()
        created = client.post(BOOKINGS_URL, {'listing': listing.id, 'start_date': start, 'end_date': end})
        response = client.get(f'{BOOKINGS_URL}{created.data["id"]}/')
        assert response.status_code == status.HTTP_200_OK

    def test_listing_owner_can_view_booking(self, tenant_client, lessor_client, listing):
        """The lessor who owns the listing must be able to view the booking."""
        client, _ = tenant_client
        start, end = future_dates()
        created = client.post(BOOKINGS_URL, {'listing': listing.id, 'start_date': start, 'end_date': end})
        lessor, _ = lessor_client
        response = lessor.get(f'{BOOKINGS_URL}{created.data["id"]}/')
        assert response.status_code == status.HTTP_200_OK

    def test_unrelated_user_cannot_view_booking(self, tenant_client, tenant_client_2, listing):
        """A tenant with no relation to the booking must receive 403."""
        client, _ = tenant_client
        start, end = future_dates()
        created = client.post(BOOKINGS_URL, {'listing': listing.id, 'start_date': start, 'end_date': end})
        other, _ = tenant_client_2
        response = other.get(f'{BOOKINGS_URL}{created.data["id"]}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBookingStatusUpdate:

    def _create_booking(self, client, listing_id, start_offset=10, length=3):
        start, end = future_dates(start_offset=start_offset, length=length)
        response = client.post(BOOKINGS_URL, {'listing': listing_id, 'start_date': start, 'end_date': end})
        return response.data['id']

    def test_lessor_confirms_pending_booking(self, tenant_client, lessor_client, listing):
        """Listing owner must be able to confirm a pending booking."""
        tenant, _ = tenant_client
        booking_id = self._create_booking(tenant, listing.id)
        lessor, _ = lessor_client
        response = lessor.patch(f'{BOOKINGS_URL}{booking_id}/status/', {'status': BookingStatus.CONFIRMED})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == BookingStatus.CONFIRMED

    def test_lessor_rejects_pending_booking(self, tenant_client, lessor_client, listing):
        """Listing owner must be able to reject a pending booking."""
        tenant, _ = tenant_client
        booking_id = self._create_booking(tenant, listing.id)
        lessor, _ = lessor_client
        response = lessor.patch(f'{BOOKINGS_URL}{booking_id}/status/', {'status': BookingStatus.REJECTED})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == BookingStatus.REJECTED

    def test_tenant_cannot_confirm_403(self, tenant_client, listing):
        """Tenant must not be able to confirm their own booking."""
        booking_id = self._create_booking(tenant_client[0], listing.id)
        response = tenant_client[0].patch(f'{BOOKINGS_URL}{booking_id}/status/', {'status': BookingStatus.CONFIRMED})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_other_lessor_cannot_confirm_403(self, tenant_client, lessor_client_2, listing):
        """A lessor who does not own the listing must not confirm the booking."""
        booking_id = self._create_booking(tenant_client[0], listing.id)
        other_lessor, _ = lessor_client_2
        response = other_lessor.patch(f'{BOOKINGS_URL}{booking_id}/status/', {'status': BookingStatus.CONFIRMED})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_lessor_cannot_cancel_403(self, tenant_client, lessor_client, listing):
        """Lessor must not be able to cancel a booking; only the tenant can."""
        tenant, _ = tenant_client
        booking_id = self._create_booking(tenant, listing.id)
        lessor, _ = lessor_client
        response = lessor.patch(f'{BOOKINGS_URL}{booking_id}/status/', {'status': BookingStatus.CANCELED})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_tenant_cancels_with_enough_lead_time(self, tenant_client, listing):
        """Tenant must be able to cancel a pending booking 2+ days before start."""
        tenant, _ = tenant_client
        booking_id = self._create_booking(tenant, listing.id, start_offset=10)
        response = tenant.patch(f'{BOOKINGS_URL}{booking_id}/status/', {'status': BookingStatus.CANCELED})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == BookingStatus.CANCELED

    def test_tenant_cancel_too_late_400(self, tenant_client, listing):
        """Cancellation less than 2 days before start must be rejected."""
        tenant, _ = tenant_client
        booking_id = self._create_booking(tenant, listing.id, start_offset=1)
        response = tenant.patch(f'{BOOKINGS_URL}{booking_id}/status/', {'status': BookingStatus.CANCELED})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_double_confirm_400(self, tenant_client, lessor_client, listing):
        """Confirming an already confirmed booking must fail."""
        tenant, _ = tenant_client
        booking_id = self._create_booking(tenant, listing.id)
        lessor, _ = lessor_client
        lessor.patch(f'{BOOKINGS_URL}{booking_id}/status/', {'status': BookingStatus.CONFIRMED})
        response = lessor.patch(f'{BOOKINGS_URL}{booking_id}/status/', {'status': BookingStatus.CONFIRMED})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_check_in_after_confirmed(self, tenant_client, lessor_client, listing):
        """Check-in must succeed only after the booking is confirmed."""
        tenant, _ = tenant_client
        booking_id = self._create_booking(tenant, listing.id)
        lessor, _ = lessor_client
        lessor.patch(f'{BOOKINGS_URL}{booking_id}/status/', {'status': BookingStatus.CONFIRMED})
        response = lessor.patch(f'{BOOKINGS_URL}{booking_id}/status/', {'status': BookingStatus.CHECKED_IN})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == BookingStatus.CHECKED_IN

    def test_check_in_from_pending_400(self, tenant_client, lessor_client, listing):
        """Check-in must fail if the booking was never confirmed."""
        tenant, _ = tenant_client
        booking_id = self._create_booking(tenant, listing.id)
        lessor, _ = lessor_client
        response = lessor.patch(f'{BOOKINGS_URL}{booking_id}/status/', {'status': BookingStatus.CHECKED_IN})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestBookingServiceUnit:

    def test_confirm_by_non_owner_raises_permission_denied(self, tenant_client, lessor_client_2, listing):
        """Service layer must raise PermissionDenied for a non-owner lessor."""
        _, tenant = tenant_client
        booking = Booking.objects.create(
            listing=listing, tenant=tenant, start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=8),
        )
        _, other_lessor = lessor_client_2
        with pytest.raises(PermissionDenied):
            BookingService.confirm_booking(booking, other_lessor)
