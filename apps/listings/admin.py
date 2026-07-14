from django.contrib import admin

from apps.listings.models import Listing, ListingPhoto


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """Admin configuration for Listing model."""

    list_display = ['title', 'owner', 'city', 'price', 'property_type', 'is_active', 'is_deleted', 'created_at']
    list_filter = ['is_active', ('deleted_at', admin.EmptyFieldListFilter), 'property_type', 'city']
    search_fields = ['title', 'description', 'city']
    readonly_fields = ['views_count', 'average_rating', 'reviews_count', 'created_at', 'updated_at']


@admin.register(ListingPhoto)
class ListingPhotoAdmin(admin.ModelAdmin):
    """Admin configuration for ListingPhoto model."""

    list_display = ['id', 'listing', 'is_primary', 'created_at']
    list_filter = ['is_primary']
