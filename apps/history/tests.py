import os

import pytest
from rest_framework import status

from apps.history.models import SearchHistory, ViewHistory
from apps.history.services.search_history import SearchHistoryService
from apps.history.services.view_history import ViewHistoryService

LISTINGS_URL = '/api/v1/listings/'


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
