import io
import os
from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework import status

from apps.listings.models import Listing, ListingPhoto, PropertyType

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

    def test_only_active_listings_visible(self, api_client, listing, inactive_listing):
        """Inactive listings must not appear in public list."""
        response = api_client.get(LISTINGS_URL)
        ids = [r['id'] for r in response.data['results']]
        assert listing.id in ids
        assert inactive_listing.id not in ids

    def test_deleted_listing_hidden(self, api_client, listing):
        """Soft-deleted listings must not appear in public list."""
        listing.is_deleted = True
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
        listing.is_deleted = True
        listing.save()
        response = api_client.get(f'{LISTINGS_URL}{listing.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_nonexistent_listing_returns_404(self, api_client):
        """Non-existent ID must return 404."""
        response = api_client.get(f'{LISTINGS_URL}99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


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
