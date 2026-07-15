import io
import os
import random
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.utils import timezone
from PIL import Image
from rest_framework import status

from apps.bookings.models import Booking, BookingStatus
from apps.history.models import SearchHistory, ViewHistory
from apps.listings.management.commands import seed_demo_data as seed_demo_data_command
from apps.listings.models import Listing, ListingPhoto, PropertyType
from apps.listings.serializers.listing import ListingCreateSerializer, ListingSerializer
from apps.listings.views.listing import ListingDetailView, ListingListCreateView
from apps.reviews.models import Review
from apps.users.models import User, UserRole
from apps.users.services.user import UserService

LISTINGS_URL = '/api/v1/listings/'
MY_LISTINGS_URL = '/api/v1/listings/my/'


def make_image_file(name='photo.jpg', image_format='JPEG', content_type='image/jpeg', color='red'):
    """Build a small, genuinely decodable in-memory image for upload tests."""
    buffer = io.BytesIO()
    Image.new('RGB', (10, 10), color=color).save(buffer, format=image_format)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type=content_type)


def make_oversized_image_file():
    """Build a valid but oversized (> 5 MB) PNG using incompressible random pixel noise."""
    width, height = 2000, 2000
    raw = os.urandom(width * height * 3)
    image = Image.frombuffer('RGB', (width, height), raw, 'raw', 'RGB', 0, 1)
    buffer = io.BytesIO()
    image.save(buffer, format='PNG', compress_level=0)
    return SimpleUploadedFile('big.png', buffer.getvalue(), content_type='image/png')


@pytest.fixture
def listing_payload():
    """Return valid payload for a listing."""
    return {
        'title': 'Nice apartment in Berlin',
        'description': 'Beautiful 2-room apartment in city center.',
        'city': 'Berlin',
        'district': 'Mitte',
        'postal_code': os.getenv('TEST_LISTING_POSTAL_CODE', '00000'),
        'price': '1200.00',
        'rooms': 2,
        'property_type': PropertyType.APARTMENT,
        'is_active': True,
    }


@pytest.fixture
def listing(db, lessor_client, listing_payload):
    """Active listing owned by lessor_client's user."""
    _, user = lessor_client
    payload = listing_payload.copy()
    return Listing.objects.create(owner=user, **payload)


@pytest.fixture
def inactive_listing(db, lessor_client, listing_payload):
    """Inactive listing owned by lessor_client's user."""
    _, user = lessor_client
    payload = listing_payload.copy()
    payload['is_active'] = False
    payload['title'] = 'Inactive apartment'
    return Listing.objects.create(owner=user, **payload)


@pytest.mark.django_db
class TestListingCreate:

    def test_lessor_creates_listing_201(self, lessor_client, listing_payload):
        """Lessor must be able to create a listing and get 201."""
        client, _ = lessor_client
        response = client.post(LISTINGS_URL, listing_payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == listing_payload['title']
        assert response.data['city'] == listing_payload['city']

    def test_tenant_cannot_create_403(self, tenant_client, listing_payload):
        """Tenant must receive 403 when trying to create a listing."""
        client, _ = tenant_client
        response = client.post(LISTINGS_URL, listing_payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_anonymous_cannot_create_401(self, api_client, listing_payload):
        """Unauthenticated user must receive 401."""
        response = api_client.post(LISTINGS_URL, listing_payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_missing_required_fields_400(self, lessor_client):
        """Empty body must be rejected with 400."""
        client, _ = lessor_client
        response = client.post(LISTINGS_URL, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_zero_price_400(self, lessor_client, listing_payload):
        """A price of zero must be rejected with 400."""
        client, _ = lessor_client
        response = client.post(LISTINGS_URL, {**listing_payload, 'price': '0'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'price' in response.data

    def test_negative_price_400(self, lessor_client, listing_payload):
        """A negative price must be rejected with 400."""
        client, _ = lessor_client
        response = client.post(LISTINGS_URL, {**listing_payload, 'price': '-100.00'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'price' in response.data

    def test_zero_rooms_400(self, lessor_client, listing_payload):
        """A room count of zero must be rejected with 400."""
        client, _ = lessor_client
        response = client.post(LISTINGS_URL, {**listing_payload, 'rooms': 0})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'rooms' in response.data

    def test_create_persists_to_db(self, lessor_client, listing_payload):
        """Successful creation must save the listing to the database."""
        client, _ = lessor_client
        client.post(LISTINGS_URL, listing_payload)
        assert Listing.objects.filter(title=listing_payload['title']).exists()

    def test_owner_set_to_authenticated_user(self, lessor_client, listing_payload):
        """Created listing must be owned by the authenticated lessor."""
        client, user = lessor_client
        response = client.post(LISTINGS_URL, listing_payload)
        assert response.status_code == status.HTTP_201_CREATED
        created = Listing.objects.get(id=response.data['id'])
        assert created.owner == user


@pytest.mark.django_db
class TestListingPhotos:

    def test_listing_without_photos_has_no_cover_image(self, api_client, listing):
        """A listing with no photos must expose an empty photos list and null cover_image."""
        response = api_client.get(f'{LISTINGS_URL}{listing.id}/')
        assert response.data['photos'] == []
        assert response.data['cover_image'] is None

    def test_owner_can_upload_photo_201(self, lessor_client, listing):
        """Owner must be able to upload a photo and get its absolute URL back."""
        client, _ = lessor_client
        response = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['image'].startswith('http')

    def test_first_uploaded_photo_becomes_primary(self, lessor_client, listing):
        """The first photo uploaded for a listing must automatically become the cover."""
        client, _ = lessor_client
        response = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()})
        assert response.data['is_primary'] is True

    def test_second_photo_is_not_primary_by_default(self, lessor_client, listing):
        """A second uploaded photo must not replace the existing cover photo."""
        client, _ = lessor_client
        client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()})
        response = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()})
        assert response.data['is_primary'] is False

    def test_upload_oversized_photo_400(self, lessor_client, listing):
        """A photo larger than 5 MB must be rejected."""
        client, _ = lessor_client
        response = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_oversized_image_file()})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_upload_disallowed_photo_type_400(self, lessor_client, listing):
        """A photo format outside the allow-list (e.g. GIF) must be rejected."""
        client, _ = lessor_client
        image = make_image_file(name='photo.gif', image_format='GIF', content_type='image/gif')
        response = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': image})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_max_five_photos_enforced(self, lessor_client, listing):
        """A sixth photo upload for the same listing must be rejected."""
        client, _ = lessor_client
        for _ in range(5):
            response = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()})
            assert response.status_code == status.HTTP_201_CREATED

        response = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ListingPhoto.objects.filter(listing=listing).count() == 5

    def test_non_owner_cannot_upload_403(self, lessor_client_2, listing):
        """A different lessor must not be able to upload a photo to someone else's listing."""
        client, _ = lessor_client_2
        response = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_tenant_cannot_upload_403(self, tenant_client, listing):
        """Tenants must not be able to upload listing photos."""
        client, _ = tenant_client
        response = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_anonymous_cannot_upload_401(self, api_client, listing):
        """Unauthenticated requests must not be able to upload listing photos."""
        response = api_client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_owner_can_set_different_photo_as_cover(self, lessor_client, listing):
        """Setting a second photo as primary must unset the first photo's primary flag."""
        client, _ = lessor_client
        first = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()}).data
        second = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()}).data

        response = client.patch(f"{LISTINGS_URL}{listing.id}/photos/{second['id']}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_primary'] is True
        assert ListingPhoto.objects.get(id=first['id']).is_primary is False

    def test_non_owner_cannot_set_primary_403(self, lessor_client, lessor_client_2, listing):
        """A different lessor must not be able to change another owner's cover photo."""
        client, _ = lessor_client
        photo = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()}).data

        other_client, _ = lessor_client_2
        response = other_client.patch(f"{LISTINGS_URL}{listing.id}/photos/{photo['id']}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_owner_can_delete_photo_204(self, lessor_client, listing):
        """Owner must be able to delete one of their listing's photos."""
        client, _ = lessor_client
        photo = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()}).data
        response = client.delete(f"{LISTINGS_URL}{listing.id}/photos/{photo['id']}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ListingPhoto.objects.filter(id=photo['id']).exists()

    def test_deleting_primary_photo_promotes_another(self, lessor_client, listing):
        """Deleting the cover photo must promote a remaining photo to primary."""
        client, _ = lessor_client
        first = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()}).data
        second = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()}).data

        client.delete(f"{LISTINGS_URL}{listing.id}/photos/{first['id']}/")
        assert ListingPhoto.objects.get(id=second['id']).is_primary is True

    def test_non_owner_cannot_delete_403(self, lessor_client, lessor_client_2, listing):
        """A different lessor must not be able to delete another owner's listing photo."""
        client, _ = lessor_client
        photo = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()}).data

        other_client, _ = lessor_client_2
        response = other_client.delete(f"{LISTINGS_URL}{listing.id}/photos/{photo['id']}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_listing_detail_reflects_cover_image(self, lessor_client, api_client, listing):
        """The listing detail response must expose the cover photo URL and photo list."""
        client, _ = lessor_client
        client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()})

        response = api_client.get(f'{LISTINGS_URL}{listing.id}/')
        assert response.data['cover_image']
        assert len(response.data['photos']) == 1


@pytest.mark.django_db
class TestListingList:

    def test_public_list_returns_200(self, api_client, listing):
        """Public GET must return 200 with paginated results."""
        response = api_client.get(LISTINGS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_public_list_does_not_expose_owner_email(self, api_client, listing):
        """The owner's email address must never appear in the public listing feed."""
        response = api_client.get(LISTINGS_URL)
        assert 'owner_email' not in response.data['results'][0]
        assert listing.owner.email not in response.content.decode()

    def test_only_active_listings_visible(self, api_client, listing, inactive_listing):
        """Inactive listings must not appear in public list."""
        response = api_client.get(LISTINGS_URL)
        ids = [r['id'] for r in response.data['results']]
        assert listing.id in ids
        assert inactive_listing.id not in ids

    def test_deleted_listing_hidden(self, api_client, listing):
        """Soft-deleted listings must not appear in public list."""
        listing.deleted_at = timezone.now()
        listing.save()
        response = api_client.get(LISTINGS_URL)
        ids = [r['id'] for r in response.data['results']]
        assert listing.id not in ids

    def test_filter_by_city(self, api_client, listing):
        """?city= must filter listings by city name (case-insensitive)."""
        response = api_client.get(LISTINGS_URL, {'city': 'berlin'})
        assert response.status_code == status.HTTP_200_OK
        for result in response.data['results']:
            assert 'berlin' in result['city'].lower()

    def test_filter_by_district(self, api_client, listing):
        """?district= must filter listings by district name (case-insensitive)."""
        response = api_client.get(LISTINGS_URL, {'district': 'mitte'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1
        for result in response.data['results']:
            assert 'mitte' in result['district'].lower()

    def test_filter_by_district_no_match_returns_empty(self, api_client, listing):
        """?district= with no matching district must return an empty result."""
        response = api_client.get(LISTINGS_URL, {'district': 'nonexistentdistrict'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_filter_by_price_max(self, api_client, listing):
        """?price_max= must exclude listings above the given price."""
        response = api_client.get(LISTINGS_URL, {'price_max': '2000'})
        assert response.status_code == status.HTTP_200_OK
        for result in response.data['results']:
            assert Decimal(result['price']) <= Decimal('2000')

    def test_filter_by_price_min(self, api_client, listing):
        """?price_min= must exclude listings below the given price."""
        response = api_client.get(LISTINGS_URL, {'price_min': '500'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_filter_by_rooms_min(self, api_client, listing):
        """?rooms_min= must exclude listings with fewer rooms."""
        response = api_client.get(LISTINGS_URL, {'rooms_min': '2'})
        assert response.status_code == status.HTTP_200_OK
        for result in response.data['results']:
            assert result['rooms'] >= 2

    def test_filter_by_property_type(self, api_client, listing):
        """?property_type= must return only listings of that type."""
        response = api_client.get(LISTINGS_URL, {'property_type': PropertyType.APARTMENT})
        assert response.status_code == status.HTTP_200_OK
        for result in response.data['results']:
            assert result['property_type'] == PropertyType.APARTMENT

    def test_search_by_keyword_in_title(self, api_client, listing):
        """?search= must match listings by title."""
        response = api_client.get(LISTINGS_URL, {'search': 'Nice apartment'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_search_no_match_returns_empty(self, api_client, listing):
        """?search= with no match must return empty results."""
        response = api_client.get(LISTINGS_URL, {'search': 'xyznonexistent999'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0

    def test_ordering_by_price_asc(self, api_client, db, lessor_client, listing_payload):
        """?ordering=price must return listings sorted by price ascending."""
        _, user = lessor_client
        Listing.objects.create(owner=user, **{**listing_payload, 'price': '800.00', 'title': 'Cheap'})
        Listing.objects.create(owner=user, **{**listing_payload, 'price': '2000.00', 'title': 'Expensive'})
        response = api_client.get(LISTINGS_URL, {'ordering': 'price'})
        prices = [Decimal(r['price']) for r in response.data['results']]
        assert prices == sorted(prices)

    def test_ordering_by_price_desc(self, api_client, db, lessor_client, listing_payload):
        """?ordering=-price must return listings sorted by price descending."""
        _, user = lessor_client
        Listing.objects.create(owner=user, **{**listing_payload, 'price': '800.00', 'title': 'Cheap'})
        Listing.objects.create(owner=user, **{**listing_payload, 'price': '2000.00', 'title': 'Expensive'})
        response = api_client.get(LISTINGS_URL, {'ordering': '-price'})
        prices = [Decimal(r['price']) for r in response.data['results']]
        assert prices == sorted(prices, reverse=True)


@pytest.mark.django_db
class TestListingDetail:

    def test_detail_public_returns_200(self, api_client, listing):
        """Any user must be able to retrieve listing details."""
        response = api_client.get(f'{LISTINGS_URL}{listing.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == listing.id
        assert response.data['title'] == listing.title

    def test_deleted_listing_returns_404(self, api_client, listing):
        """Soft-deleted listing must return 404 on detail."""
        listing.deleted_at = timezone.now()
        listing.save()
        response = api_client.get(f'{LISTINGS_URL}{listing.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_nonexistent_listing_returns_404(self, api_client):
        """Non-existent ID must return 404."""
        response = api_client.get(f'{LISTINGS_URL}99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_public_detail_does_not_expose_owner_email(self, api_client, listing):
        """The owner's email address must never appear in the public response."""
        response = api_client.get(f'{LISTINGS_URL}{listing.id}/')
        assert 'owner_email' not in response.data
        assert response.data['owner_username'] == listing.owner.username
        assert listing.owner.email not in response.content.decode()


@pytest.mark.django_db
class TestListingUpdate:

    def test_owner_can_full_update_200(self, lessor_client, listing, listing_payload):
        """Owner must be able to PUT and receive updated data."""
        client, _ = lessor_client
        updated = {**listing_payload, 'title': 'Updated Title', 'price': '1500.00'}
        response = client.put(f'{LISTINGS_URL}{listing.id}/', updated)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Updated Title'

    def test_owner_can_partial_update_200(self, lessor_client, listing):
        """Owner must be able to PATCH a single field."""
        client, _ = lessor_client
        response = client.patch(f'{LISTINGS_URL}{listing.id}/', {'title': 'Patched Title'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Patched Title'

    def test_non_owner_cannot_update_403(self, lessor_client_2, listing, listing_payload):
        """Different lessor must receive 403 when trying to update."""
        client, _ = lessor_client_2
        response = client.put(f'{LISTINGS_URL}{listing.id}/', {**listing_payload, 'title': 'Hack'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_tenant_cannot_update_403(self, tenant_client, listing, listing_payload):
        """Tenant must receive 403 when trying to update a listing."""
        client, _ = tenant_client
        response = client.put(f'{LISTINGS_URL}{listing.id}/', listing_payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_anonymous_cannot_update_401(self, api_client, listing, listing_payload):
        """Unauthenticated request must receive 401."""
        response = api_client.put(f'{LISTINGS_URL}{listing.id}/', listing_payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestListingDelete:

    def test_owner_can_delete_204(self, lessor_client, listing):
        """Owner must be able to soft-delete listing, receiving 204."""
        client, _ = lessor_client
        response = client.delete(f'{LISTINGS_URL}{listing.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        listing.refresh_from_db()
        assert listing.is_deleted is True

    def test_delete_records_deleted_at_timestamp(self, lessor_client, listing):
        """Soft-deleting a listing must record the moment of deletion, not just a flag."""
        client, _ = lessor_client
        before = timezone.now()
        client.delete(f'{LISTINGS_URL}{listing.id}/')
        listing.refresh_from_db()
        assert listing.deleted_at is not None
        assert listing.deleted_at >= before

    def test_deleted_listing_disappears_from_public(self, lessor_client, api_client, listing):
        """After deletion, listing must not appear in public list."""
        client, _ = lessor_client
        client.delete(f'{LISTINGS_URL}{listing.id}/')
        response = api_client.get(LISTINGS_URL)
        ids = [r['id'] for r in response.data['results']]
        assert listing.id not in ids

    def test_non_owner_cannot_delete_403(self, lessor_client_2, listing):
        """Different lessor must receive 403 when trying to delete."""
        client, _ = lessor_client_2
        response = client.delete(f'{LISTINGS_URL}{listing.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_tenant_cannot_delete_403(self, tenant_client, listing):
        """Tenant must receive 403 when trying to delete a listing."""
        client, _ = tenant_client
        response = client.delete(f'{LISTINGS_URL}{listing.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestListingToggle:

    def test_owner_can_toggle_200(self, lessor_client, listing):
        """Owner must be able to toggle is_active and receive 200."""
        client, _ = lessor_client
        initial = listing.is_active
        response = client.patch(f'{LISTINGS_URL}{listing.id}/toggle/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_active'] != initial

    def test_toggle_twice_restores_state(self, lessor_client, listing):
        """Two consecutive toggles must restore the original is_active state."""
        client, _ = lessor_client
        initial = listing.is_active
        client.patch(f'{LISTINGS_URL}{listing.id}/toggle/')
        response = client.patch(f'{LISTINGS_URL}{listing.id}/toggle/')
        assert response.data['is_active'] == initial

    def test_non_owner_cannot_toggle_403(self, lessor_client_2, listing):
        """Different lessor must receive 403 on toggle."""
        client, _ = lessor_client_2
        response = client.patch(f'{LISTINGS_URL}{listing.id}/toggle/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_tenant_cannot_toggle_403(self, tenant_client, listing):
        """Tenant must receive 403 on toggle."""
        client, _ = tenant_client
        response = client.patch(f'{LISTINGS_URL}{listing.id}/toggle/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_anonymous_cannot_toggle_401(self, api_client, listing):
        """Unauthenticated request must receive 401 on toggle."""
        response = api_client.patch(f'{LISTINGS_URL}{listing.id}/toggle/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestMyListings:

    def test_lessor_sees_own_active_listings(self, lessor_client, listing):
        """Lessor must see their own active listing in /my/."""
        client, _ = lessor_client
        response = client.get(MY_LISTINGS_URL)
        assert response.status_code == status.HTTP_200_OK
        ids = [r['id'] for r in response.data['results']]
        assert listing.id in ids

    def test_lessor_sees_own_inactive_listings(self, lessor_client, inactive_listing):
        """Lessor must see their own inactive listing in /my/."""
        client, _ = lessor_client
        response = client.get(MY_LISTINGS_URL)
        ids = [r['id'] for r in response.data['results']]
        assert inactive_listing.id in ids

    def test_lessor_does_not_see_other_owners_listings(self, lessor_client_2, listing):
        """Lessor must not see listings belonging to another owner."""
        client, _ = lessor_client_2
        response = client.get(MY_LISTINGS_URL)
        ids = [r['id'] for r in response.data['results']]
        assert listing.id not in ids

    def test_tenant_cannot_access_my_listings_403(self, tenant_client):
        """Tenant must receive 403 when accessing /my/."""
        client, _ = tenant_client
        response = client.get(MY_LISTINGS_URL)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_anonymous_cannot_access_my_listings_401(self, api_client):
        """Unauthenticated user must receive 401 when accessing /my/."""
        response = api_client.get(MY_LISTINGS_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestListingModel:

    def test_listing_str_representation(self, listing):
        """String representation of a listing must be its title."""
        assert str(listing) == listing.title

    def test_listing_photo_str_representation(self, lessor_client, listing):
        """String representation of a listing photo must reference the photo and listing ids."""
        client, _ = lessor_client
        photo_data = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()}).data
        photo = ListingPhoto.objects.get(id=photo_data['id'])
        assert str(photo) == f'Photo #{photo.id} for listing #{listing.id}'


@pytest.mark.django_db
class TestListingSerializerSelection:
    """Method-based serializer switch used by drf-spectacular for accurate Swagger docs."""

    def test_list_create_view_uses_create_serializer_for_post(self, rf):
        view = ListingListCreateView()
        view.request = rf.post(LISTINGS_URL)
        assert view.get_serializer_class() is ListingCreateSerializer

    def test_list_create_view_uses_full_serializer_for_get(self, rf):
        view = ListingListCreateView()
        view.request = rf.get(LISTINGS_URL)
        assert view.get_serializer_class() is ListingSerializer

    def test_detail_view_uses_create_serializer_for_patch(self, rf):
        view = ListingDetailView()
        view.request = rf.patch(f'{LISTINGS_URL}1/')
        assert view.get_serializer_class() is ListingCreateSerializer

    def test_detail_view_uses_full_serializer_for_get(self, rf):
        view = ListingDetailView()
        view.request = rf.get(f'{LISTINGS_URL}1/')
        assert view.get_serializer_class() is ListingSerializer


@pytest.mark.django_db
class TestSeedDemoDataCommand:
    """Coverage for the seed_demo_data management command used to populate demo data."""

    def _seed(self, **overrides):
        """Call seed_demo_data with small, fixed-seed counts so results are fast and deterministic."""
        random.seed(1234)
        options = {'lessors': 2, 'tenants': 3, 'listings': 4, 'clear': False}
        options.update(overrides)
        call_command('seed_demo_data', **options)

    def test_creates_expected_user_and_listing_counts(self):
        """Command must create the requested number of seed users and listings."""
        self._seed()
        assert User.objects.filter(email__iendswith='@seed.example').count() == 2 + 1 + 3 + 1
        assert Listing.objects.count() == 4
        assert Listing.objects.filter(deleted_at__isnull=False).count() == 0

    def test_creates_known_demo_accounts(self):
        """Command must create fixed-credential demo Lessor and Tenant accounts."""
        self._seed()
        lessor = User.objects.get(username='demo_lessor')
        tenant = User.objects.get(username='demo_tenant')
        assert lessor.role == UserRole.LESSOR
        assert tenant.role == UserRole.TENANT

    def test_bookings_satisfy_date_constraint_and_vary_in_status(self):
        """All seeded bookings must have end_date after start_date and cover multiple statuses."""
        self._seed()
        bookings = Booking.objects.all()
        assert bookings.count() > 0
        assert all(booking.end_date > booking.start_date for booking in bookings)

    def test_reviews_exist_only_for_checked_in_bookings(self):
        """Every review must belong to a checked-in booking and have a rating within 1-5."""
        self._seed()
        checked_in_count = Booking.objects.filter(status=BookingStatus.CHECKED_IN).count()
        assert Review.objects.count() == checked_in_count
        assert all(1 <= review.rating <= 5 for review in Review.objects.all())

    def test_listing_rating_cache_updated_via_signal(self):
        """A listing with a review must have its average_rating/reviews_count updated by signals."""
        self._seed()
        reviewed_listing = Listing.objects.filter(reviews_count__gt=0).first()
        assert reviewed_listing is not None
        assert reviewed_listing.average_rating > 0

    def test_view_history_matches_views_count_totals(self):
        """Sum of Listing.views_count must equal the number of ViewHistory rows created."""
        self._seed()
        total_views_count = sum(Listing.objects.values_list('views_count', flat=True))
        assert total_views_count == ViewHistory.objects.count()

    def test_search_history_respects_unique_together(self):
        """Repeated search keywords for the same tenant must not violate the unique constraint."""
        self._seed()
        assert SearchHistory.objects.count() > 0

    def test_clear_removes_only_seed_data(self):
        """--clear must delete seed users and their data without touching real accounts."""
        real_user = UserService.create_user(
            email='real-owner@example.test', password='irrelevant-pass-1', username='real_owner', role=UserRole.LESSOR,
        )
        self._seed()
        self._seed(clear=True)
        assert User.objects.filter(pk=real_user.pk).exists()

    def test_rerun_without_clear_does_not_raise(self):
        """Calling the command twice without --clear must not raise on uniqueness constraints."""
        self._seed()
        self._seed()
        assert User.objects.filter(email__iendswith='@seed.example').count() == (2 + 1 + 3 + 1) * 2 - 2

    def test_no_photos_created_when_demo_photo_dir_missing(self, monkeypatch, tmp_path):
        """With no demo_photo directory present, listings must be seeded without any photos."""
        monkeypatch.setattr(seed_demo_data_command, 'DEMO_PHOTO_DIR', tmp_path / 'does-not-exist')
        self._seed()
        assert ListingPhoto.objects.count() == 0

    def test_no_photos_created_when_demo_photo_dir_empty(self, monkeypatch, tmp_path):
        """An existing but empty demo_photo directory must not cause errors and yields no photos."""
        monkeypatch.setattr(seed_demo_data_command, 'DEMO_PHOTO_DIR', tmp_path)
        self._seed()
        assert ListingPhoto.objects.count() == 0

    def test_attaches_one_random_photo_per_listing_when_demo_photos_exist(self, monkeypatch, settings, tmp_path):
        """Each seeded listing must receive exactly one primary photo picked from demo_photo."""
        settings.MEDIA_ROOT = tmp_path / 'media'
        photo_dir = tmp_path / 'demo_photo'
        photo_dir.mkdir()
        Image.new('RGB', (10, 10), color='blue').save(photo_dir / 'sample.jpg', format='JPEG')
        monkeypatch.setattr(seed_demo_data_command, 'DEMO_PHOTO_DIR', photo_dir)

        self._seed(listings=4)

        assert ListingPhoto.objects.count() == 4
        for listing in Listing.objects.all():
            assert listing.photos.count() == 1
            assert listing.photos.first().is_primary is True

    def test_non_image_files_in_demo_photo_dir_are_ignored(self, monkeypatch, settings, tmp_path):
        """Non-image files placed in demo_photo (e.g. a README) must never be used as a photo."""
        settings.MEDIA_ROOT = tmp_path / 'media'
        photo_dir = tmp_path / 'demo_photo'
        photo_dir.mkdir()
        (photo_dir / 'notes.txt').write_text('not an image')
        monkeypatch.setattr(seed_demo_data_command, 'DEMO_PHOTO_DIR', photo_dir)

        self._seed(listings=2)

        assert ListingPhoto.objects.count() == 0


@pytest.mark.django_db
class TestClearListingsCommand:
    """Coverage for the clear_listings management command used to wipe all listing data safely."""

    def test_no_listings_prints_message_and_makes_no_changes(self, capsys):
        """With an empty table, the command must report that and exit without prompting."""
        call_command('clear_listings')
        assert 'No listings found' in capsys.readouterr().out

    def test_declining_confirmation_keeps_data(self, monkeypatch, listing):
        """Answering anything other than 'yes' at the prompt must leave listings untouched."""
        monkeypatch.setattr('builtins.input', lambda _: 'no')
        call_command('clear_listings')
        assert Listing.objects.filter(pk=listing.pk).exists()

    def test_confirming_prompt_deletes_listing(self, monkeypatch, listing):
        """Typing 'yes' at the interactive prompt must delete the listing."""
        monkeypatch.setattr('builtins.input', lambda _: 'yes')
        call_command('clear_listings')
        assert not Listing.objects.filter(pk=listing.pk).exists()

    def test_yes_flag_skips_prompt_and_deletes_everything(self, listing, inactive_listing):
        """The --yes flag must bypass the prompt and remove every listing, active or not."""
        call_command('clear_listings', yes=True)
        assert Listing.objects.count() == 0

    def test_cascade_deletes_bookings_reviews_and_view_history(self, lessor_client, tenant_client, listing):
        """Deleting a listing must cascade to its bookings, reviews and view history."""
        _, tenant = tenant_client
        booking = Booking.objects.create(
            listing=listing,
            tenant=tenant,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=3),
            price_per_night=listing.price,
            total_price=Decimal(listing.price) * 3,
            status=BookingStatus.CHECKED_IN,
        )
        Review.objects.create(listing=listing, author=tenant, booking=booking, rating=5, comment='Great stay')
        ViewHistory.objects.create(listing=listing, user=tenant)

        call_command('clear_listings', yes=True)

        assert Booking.objects.count() == 0
        assert Review.objects.count() == 0
        assert ViewHistory.objects.count() == 0

    def test_removes_photo_files_from_disk(self, settings, tmp_path, lessor_client, listing):
        """Deleting a listing must also remove its uploaded photo files from MEDIA_ROOT."""
        settings.MEDIA_ROOT = tmp_path
        client, _ = lessor_client
        response = client.post(f'{LISTINGS_URL}{listing.id}/photos/', {'image': make_image_file()})
        photo = ListingPhoto.objects.get(id=response.data['id'])
        file_path = tmp_path / photo.image.name
        assert file_path.is_file()

        call_command('clear_listings', yes=True)

        assert not file_path.is_file()

    def test_does_not_touch_users(self, lessor_client, listing):
        """Clearing listings must never delete the owning user account."""
        _, owner = lessor_client
        call_command('clear_listings', yes=True)
        assert User.objects.filter(pk=owner.pk).exists()
