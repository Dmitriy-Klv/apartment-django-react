import os
from datetime import date, timedelta

import pytest
from django.db import IntegrityError, transaction
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.bookings.models import Booking, BookingStatus
from apps.listings.models import Listing, PropertyType
from apps.reviews.models import Review
from apps.users.models import User, UserRole


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
        title='Apartment in Hamburg',
        description='Bright 1-room apartment.',
        city='Hamburg',
        district='Altona',
        postal_code=os.getenv('TEST_LISTING_POSTAL_CODE', '00000'),
        price='850.00',
        rooms=1,
        property_type=PropertyType.APARTMENT,
        is_active=True,
    )


def checked_in_booking(listing, tenant, offset=10):
    """Create a completed (checked-in) booking eligible for a review."""
    start = date.today() - timedelta(days=offset)
    return Booking.objects.create(
        listing=listing, tenant=tenant, start_date=start, end_date=start + timedelta(days=3),
        status=BookingStatus.CHECKED_IN,
    )


@pytest.mark.django_db
class TestReviewUniqueness:

    def test_one_review_per_booking(self, tenant_client, listing):
        """A single booking must not be reviewed twice."""
        _, tenant = tenant_client
        booking = checked_in_booking(listing, tenant)
        Review.objects.create(listing=listing, author=tenant, booking=booking, rating=5, comment='Great stay')
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Review.objects.create(listing=listing, author=tenant, booking=booking, rating=4, comment='Again')

    def test_same_tenant_can_review_two_separate_bookings_on_same_listing(self, tenant_client, listing):
        """A tenant who stayed twice must be able to leave a review for each booking."""
        _, tenant = tenant_client
        first_booking = checked_in_booking(listing, tenant, offset=30)
        second_booking = checked_in_booking(listing, tenant, offset=10)
        Review.objects.create(listing=listing, author=tenant, booking=first_booking, rating=4, comment='Good stay')
        Review.objects.create(listing=listing, author=tenant, booking=second_booking, rating=5, comment='Even better')
        assert Review.objects.filter(listing=listing, author=tenant).count() == 2


@pytest.mark.django_db
class TestListingRatingSignals:

    def test_rating_and_count_update_on_review_create(self, tenant_client, tenant_client_2, listing):
        """Creating reviews must update the listing's cached average_rating and reviews_count."""
        _, tenant1 = tenant_client
        _, tenant2 = tenant_client_2
        booking1 = checked_in_booking(listing, tenant1, offset=10)
        booking2 = checked_in_booking(listing, tenant2, offset=5)

        Review.objects.create(listing=listing, author=tenant1, booking=booking1, rating=4, comment='Good')
        listing.refresh_from_db()
        assert listing.reviews_count == 1
        assert listing.average_rating == 4

        Review.objects.create(listing=listing, author=tenant2, booking=booking2, rating=2, comment='Meh')
        listing.refresh_from_db()
        assert listing.reviews_count == 2
        assert listing.average_rating == 3

    def test_rating_updates_on_review_delete(self, tenant_client, tenant_client_2, listing):
        """Deleting a review must recalculate the listing's rating cache."""
        _, tenant1 = tenant_client
        _, tenant2 = tenant_client_2
        booking1 = checked_in_booking(listing, tenant1, offset=10)
        booking2 = checked_in_booking(listing, tenant2, offset=5)

        review1 = Review.objects.create(listing=listing, author=tenant1, booking=booking1, rating=4, comment='Good')
        Review.objects.create(listing=listing, author=tenant2, booking=booking2, rating=2, comment='Meh')

        review1.delete()
        listing.refresh_from_db()
        assert listing.reviews_count == 1
        assert listing.average_rating == 2

    def test_rating_resets_when_all_reviews_removed(self, tenant_client, listing):
        """Removing the last review must reset average_rating and reviews_count to zero."""
        _, tenant = tenant_client
        booking = checked_in_booking(listing, tenant)
        review = Review.objects.create(listing=listing, author=tenant, booking=booking, rating=5, comment='Great')

        review.delete()
        listing.refresh_from_db()
        assert listing.reviews_count == 0
        assert listing.average_rating == 0
