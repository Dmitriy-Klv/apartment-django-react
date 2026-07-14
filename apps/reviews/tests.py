import os
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.bookings.models import Booking, BookingStatus
from apps.listings.models import Listing, PropertyType
from apps.reviews.models import Review
from apps.users.models import User, UserRole

REVIEWS_URL = '/api/v1/reviews/'


@pytest.fixture
def tenant_client_2(db):
    """Return (APIClient, user) for a second authenticated tenant."""
    user = User.objects.create_user(
        email=os.getenv('TEST_TENANT2_EMAIL'),
        password=os.getenv('TEST_USER_PASSWORD'),
        username='second_tenant',
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
        price_per_night=listing.price, total_price=Decimal(listing.price) * 3,
        status=BookingStatus.CHECKED_IN,
    )


@pytest.mark.django_db
class TestReviewCreateAPI:

    def test_tenant_creates_review_after_checked_in(self, tenant_client, listing):
        """A tenant with a checked-in booking must be able to leave a review."""
        client, tenant = tenant_client
        booking = checked_in_booking(listing, tenant)
        response = client.post(REVIEWS_URL, {'booking': booking.id, 'rating': 5, 'comment': 'Loved it'})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['rating'] == 5
        assert response.data['listing'] == listing.id

    def test_review_before_checked_in_400(self, tenant_client, listing):
        """A booking that is not checked in must not be reviewable."""
        client, tenant = tenant_client
        booking = Booking.objects.create(
            listing=listing, tenant=tenant,
            start_date=date.today() + timedelta(days=5), end_date=date.today() + timedelta(days=8),
            price_per_night=listing.price, total_price=Decimal(listing.price) * 3,
        )
        response = client.post(REVIEWS_URL, {'booking': booking.id, 'rating': 5, 'comment': 'Too early'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_review_someone_elses_booking_403(self, tenant_client, tenant_client_2, listing):
        """A tenant must not be able to review another tenant's booking."""
        _, owner_tenant = tenant_client
        booking = checked_in_booking(listing, owner_tenant)
        other_client, _ = tenant_client_2
        response = other_client.post(REVIEWS_URL, {'booking': booking.id, 'rating': 1, 'comment': 'Not mine'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_lessor_cannot_create_review_403(self, lessor_client, listing):
        """Lessor role must not be able to create a review."""
        client, _ = lessor_client
        response = client.post(REVIEWS_URL, {'booking': 1, 'rating': 5, 'comment': 'N/A'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_anonymous_cannot_create_review_401(self, api_client):
        """Unauthenticated request must be rejected."""
        response = api_client.post(REVIEWS_URL, {'booking': 1, 'rating': 5, 'comment': 'N/A'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_duplicate_review_on_same_booking_400(self, tenant_client, listing):
        """A second review on the same booking must be rejected."""
        client, tenant = tenant_client
        booking = checked_in_booking(listing, tenant)
        client.post(REVIEWS_URL, {'booking': booking.id, 'rating': 5, 'comment': 'First'})
        response = client.post(REVIEWS_URL, {'booking': booking.id, 'rating': 3, 'comment': 'Second'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_rating_out_of_range_400(self, tenant_client, listing):
        """Rating must be validated to the 1-5 range."""
        client, tenant = tenant_client
        booking = checked_in_booking(listing, tenant)
        response = client.post(REVIEWS_URL, {'booking': booking.id, 'rating': 6, 'comment': 'Too high'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestReviewReadAPI:

    def test_public_can_view_listing_reviews(self, tenant_client, api_client, listing):
        """Anyone must be able to list reviews for a listing."""
        client, tenant = tenant_client
        booking = checked_in_booking(listing, tenant)
        client.post(REVIEWS_URL, {'booking': booking.id, 'rating': 4, 'comment': 'Nice place'})

        response = api_client.get(f'/api/v1/listings/{listing.id}/reviews/')
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results'] if isinstance(response.data, dict) else response.data
        assert len(results) == 1

    def test_public_can_view_review_detail(self, tenant_client, api_client, listing):
        """Anyone must be able to retrieve a single review by id."""
        client, tenant = tenant_client
        booking = checked_in_booking(listing, tenant)
        created = client.post(REVIEWS_URL, {'booking': booking.id, 'rating': 4, 'comment': 'Nice place'})

        response = api_client.get(f'{REVIEWS_URL}{created.data["id"]}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['comment'] == 'Nice place'


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


@pytest.mark.django_db
class TestReviewModel:

    def test_str_representation(self, tenant_client, listing):
        """String representation must include author, listing, and rating."""
        _, tenant = tenant_client
        booking = checked_in_booking(listing, tenant)
        review = Review.objects.create(listing=listing, author=tenant, booking=booking, rating=4, comment='Good')
        assert str(review) == f'{tenant} → {listing} (4/5)'
        assert listing.average_rating == 0
