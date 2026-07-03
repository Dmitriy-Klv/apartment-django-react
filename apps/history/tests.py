import os

import pytest
from rest_framework import status

from apps.history.models import SearchHistory, ViewHistory
from apps.history.services.search_history import SearchHistoryService
from apps.history.services.view_history import ViewHistoryService

LISTINGS_URL = '/api/v1/listings/'
POPULAR_SEARCHES_URL = '/api/v1/history/searches/popular/'
POPULAR_LISTINGS_URL = '/api/v1/history/listings/popular/'


@pytest.fixture
def listing_payload():
    """Return valid payload for creating a listing."""
    return {
        'title': 'Apartment in Munich',
        'description': 'Cozy studio near the center.',
        'city': 'Munich',
        'district': 'Schwabing',
        'postal_code': os.getenv('TEST_LISTING_POSTAL_CODE', '00000'),
        'price': '900.00',
        'rooms': 1,
        'property_type': 'studio',
        'is_active': True,
    }


@pytest.fixture
def listing(db, lessor_client, listing_payload):
    """Active listing owned by lessor_client's user."""
    from apps.listings.models import Listing
    _, user = lessor_client
    return Listing.objects.create(owner=user, **listing_payload)


@pytest.mark.django_db
class TestSearchHistoryService:

    def test_first_search_creates_record(self, lessor_client):
        """First search with a keyword must create a SearchHistory record with count=1."""
        _, user = lessor_client
        SearchHistoryService.record_search(user=user, keyword='Berlin')
        obj = SearchHistory.objects.get(user=user, keyword='Berlin')
        assert obj.count == 1

    def test_repeated_search_increments_count(self, lessor_client):
        """Repeated search with the same keyword must increment the count."""
        _, user = lessor_client
        SearchHistoryService.record_search(user=user, keyword='Berlin')
        SearchHistoryService.record_search(user=user, keyword='Berlin')
        obj = SearchHistory.objects.get(user=user, keyword='Berlin')
        assert obj.count == 2

    def test_different_keywords_create_separate_records(self, lessor_client):
        """Different keywords must produce separate SearchHistory entries."""
        _, user = lessor_client
        SearchHistoryService.record_search(user=user, keyword='Berlin')
        SearchHistoryService.record_search(user=user, keyword='Munich')
        assert SearchHistory.objects.filter(user=user).count() == 2

    def test_blank_keyword_is_ignored(self, lessor_client):
        """Blank or whitespace-only keyword must not create a record."""
        _, user = lessor_client
        SearchHistoryService.record_search(user=user, keyword='   ')
        assert SearchHistory.objects.filter(user=user).count() == 0

    def test_keyword_is_trimmed(self, lessor_client):
        """Leading and trailing whitespace in keyword must be stripped."""
        _, user = lessor_client
        SearchHistoryService.record_search(user=user, keyword='  Berlin  ')
        assert SearchHistory.objects.filter(user=user, keyword='Berlin').exists()

    def test_different_users_separate_records(self, lessor_client, lessor_client_2):
        """Same keyword from two different users must create two records."""
        _, user1 = lessor_client
        _, user2 = lessor_client_2
        SearchHistoryService.record_search(user=user1, keyword='Hamburg')
        SearchHistoryService.record_search(user=user2, keyword='Hamburg')
        assert SearchHistory.objects.filter(keyword='Hamburg').count() == 2


@pytest.mark.django_db
class TestViewHistoryService:

    def test_authenticated_view_creates_record(self, lessor_client, listing):
        """Viewing a listing as authenticated user must create a ViewHistory record."""
        _, user = lessor_client
        ViewHistoryService.record_view(listing=listing, user=user)
        assert ViewHistory.objects.filter(listing=listing, user=user).count() == 1

    def test_anonymous_view_creates_record_with_null_user(self, listing):
        """Anonymous view must create a ViewHistory record with user=None."""
        ViewHistoryService.record_view(listing=listing, user=None)
        assert ViewHistory.objects.filter(listing=listing, user__isnull=True).count() == 1

    def test_multiple_views_create_multiple_records(self, lessor_client, listing):
        """Each call must create a new ViewHistory entry (log, not counter)."""
        _, user = lessor_client
        ViewHistoryService.record_view(listing=listing, user=user)
        ViewHistoryService.record_view(listing=listing, user=user)
        assert ViewHistory.objects.filter(listing=listing, user=user).count() == 2

    def test_view_increments_listing_views_count(self, lessor_client, listing):
        """Recording a view must increment the listing's cached views_count."""
        _, user = lessor_client
        ViewHistoryService.record_view(listing=listing, user=user)
        listing.refresh_from_db()
        assert listing.views_count == 1

    def test_repeated_views_accumulate_views_count(self, listing):
        """Each recorded view must add one to views_count, including anonymous views."""
        ViewHistoryService.record_view(listing=listing, user=None)
        ViewHistoryService.record_view(listing=listing, user=None)
        listing.refresh_from_db()
        assert listing.views_count == 2


@pytest.mark.django_db
class TestSearchHistoryIntegration:

    def test_authenticated_search_saves_keyword(self, lessor_client, listing):
        """GET /listings/?search= by authenticated user must save to SearchHistory."""
        client, user = lessor_client
        client.get(LISTINGS_URL, {'search': 'Apartment'})
        assert SearchHistory.objects.filter(user=user, keyword='Apartment').exists()

    def test_repeated_search_increments_count(self, lessor_client, listing):
        """Two identical searches must result in count=2."""
        client, user = lessor_client
        client.get(LISTINGS_URL, {'search': 'Munich'})
        client.get(LISTINGS_URL, {'search': 'Munich'})
        obj = SearchHistory.objects.get(user=user, keyword='Munich')
        assert obj.count == 2

    def test_anonymous_search_does_not_save(self, api_client, listing):
        """GET /listings/?search= by anonymous user must not create SearchHistory."""
        api_client.get(LISTINGS_URL, {'search': 'Berlin'})
        assert SearchHistory.objects.count() == 0

    def test_list_without_search_does_not_save(self, lessor_client, listing):
        """GET /listings/ without ?search= must not create SearchHistory."""
        client, user = lessor_client
        client.get(LISTINGS_URL)
        assert SearchHistory.objects.filter(user=user).count() == 0


@pytest.mark.django_db
class TestViewHistoryIntegration:

    def test_detail_view_creates_history_for_auth_user(self, lessor_client, listing):
        """GET /listings/{id}/ by authenticated user must create ViewHistory."""
        client, user = lessor_client
        client.get(f'{LISTINGS_URL}{listing.id}/')
        assert ViewHistory.objects.filter(listing=listing, user=user).count() == 1

    def test_detail_view_creates_history_for_anonymous(self, api_client, listing):
        """GET /listings/{id}/ by anonymous user must create ViewHistory with user=None."""
        api_client.get(f'{LISTINGS_URL}{listing.id}/')
        assert ViewHistory.objects.filter(listing=listing, user__isnull=True).count() == 1

    def test_multiple_detail_views_create_multiple_records(self, api_client, listing):
        """Each request to detail page must create a separate ViewHistory record."""
        api_client.get(f'{LISTINGS_URL}{listing.id}/')
        api_client.get(f'{LISTINGS_URL}{listing.id}/')
        assert ViewHistory.objects.filter(listing=listing).count() == 2


def results_of(response_data):
    """Return the list of results from a paginated or plain list response."""
    return response_data['results'] if isinstance(response_data, dict) else response_data


@pytest.mark.django_db
class TestPopularSearches:

    def test_popular_searches_ordered_by_total_count(self, api_client, lessor_client, lessor_client_2):
        """Popular searches must be aggregated across all users and ordered by total count descending."""
        _, user1 = lessor_client
        _, user2 = lessor_client_2
        SearchHistoryService.record_search(user=user1, keyword='Berlin')
        SearchHistoryService.record_search(user=user2, keyword='Berlin')
        SearchHistoryService.record_search(user=user1, keyword='Munich')

        response = api_client.get(POPULAR_SEARCHES_URL)
        assert response.status_code == status.HTTP_200_OK
        results = results_of(response.data)
        assert results[0]['keyword'] == 'Berlin'
        assert results[0]['total_count'] == 2
        assert results[1]['keyword'] == 'Munich'
        assert results[1]['total_count'] == 1

    def test_popular_searches_publicly_accessible(self, api_client):
        """Endpoint must be accessible without authentication."""
        response = api_client.get(POPULAR_SEARCHES_URL)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestPopularListings:

    def test_popular_listings_ordered_by_views(self, api_client, lessor_client, listing_payload):
        """Listings must be ordered by views_count descending."""
        from apps.listings.models import Listing
        _, owner = lessor_client
        popular = Listing.objects.create(owner=owner, **{**listing_payload, 'title': 'Popular', 'views_count': 10})
        unpopular = Listing.objects.create(owner=owner, **{**listing_payload, 'title': 'Unpopular', 'views_count': 1})

        response = api_client.get(POPULAR_LISTINGS_URL)
        assert response.status_code == status.HTTP_200_OK
        ids = [r['id'] for r in results_of(response.data)]
        assert ids.index(popular.id) < ids.index(unpopular.id)

    def test_inactive_listing_excluded_from_popular(self, api_client, lessor_client, listing_payload):
        """Inactive listings must not appear in the popular listings endpoint."""
        from apps.listings.models import Listing
        _, owner = lessor_client
        inactive = Listing.objects.create(
            owner=owner, **{**listing_payload, 'title': 'Inactive', 'is_active': False, 'views_count': 100},
        )

        response = api_client.get(POPULAR_LISTINGS_URL)
        ids = [r['id'] for r in results_of(response.data)]
        assert inactive.id not in ids


@pytest.mark.django_db
class TestHistoryModelStr:

    def test_search_history_str_representation(self, lessor_client):
        """String representation of a search history entry must include user, keyword, and count."""
        _, user = lessor_client
        SearchHistoryService.record_search(user=user, keyword='Berlin')
        obj = SearchHistory.objects.get(user=user, keyword='Berlin')
        assert str(obj) == f'{user} — "Berlin" (1x)'

    def test_view_history_str_representation(self, lessor_client, listing):
        """String representation of a view history entry must include user, listing, and timestamp."""
        _, user = lessor_client
        ViewHistoryService.record_view(listing=listing, user=user)
        obj = ViewHistory.objects.get(user=user, listing=listing)
        assert str(obj) == f'{user} → {listing} at {obj.viewed_at}'
