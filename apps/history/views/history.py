from django.db.models import Sum
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.history.models import SearchHistory
from apps.history.serializers.history import PopularSearchSerializer
from apps.listings.models import Listing
from apps.listings.serializers.listing import ListingSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['History'],
        summary='List popular search keywords',
        description='Publicly aggregated search keywords, ranked by total popularity across all users.',
    ),
)
class PopularSearchesView(generics.ListAPIView):
    """Return search keywords ordered by total popularity across all users."""

    serializer_class = PopularSearchSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Aggregate SearchHistory by keyword and sum counts across all users."""
        return (
            SearchHistory.objects.values('keyword')
            .annotate(total_count=Sum('count'))
            .order_by('-total_count')
        )


@extend_schema_view(
    list=extend_schema(
        tags=['History'],
        summary='List popular listings',
        description='Publicly list active listings ordered by view count, descending.',
    ),
)
class PopularListingsView(generics.ListAPIView):
    """Return active listings ordered by view count."""

    serializer_class = ListingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Return active, non-deleted listings sorted by views_count descending."""
        return Listing.objects.filter(is_active=True, deleted_at__isnull=True).prefetch_related('photos').order_by('-views_count')
