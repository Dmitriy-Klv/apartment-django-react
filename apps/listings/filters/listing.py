import django_filters

from apps.listings.models import Listing


class ListingFilter(django_filters.FilterSet):
    """Filter listings by city, price range, room count, and property type."""

    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    rooms_min = django_filters.NumberFilter(field_name='rooms', lookup_expr='gte')
    rooms_max = django_filters.NumberFilter(field_name='rooms', lookup_expr='lte')
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')

    class Meta:
        model = Listing
        fields = ['property_type', 'city', 'price_min', 'price_max', 'rooms_min', 'rooms_max']
