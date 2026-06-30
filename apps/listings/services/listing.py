from apps.listings.models import Listing


class ListingService:

    @staticmethod
    def create_listing(owner, validated_data: dict) -> Listing:
        """Create and return a new listing owned by the given user."""
        return Listing.objects.create(owner=owner, **validated_data)

    @staticmethod
    def update_listing(listing: Listing, validated_data: dict) -> Listing:
        """Apply validated data to the listing fields and persist."""
        for field, value in validated_data.items():
            setattr(listing, field, value)
        listing.save()
        return listing

    @staticmethod
    def delete_listing(listing: Listing) -> None:
        """Soft-delete a listing so bookings and reviews remain intact."""
        listing.is_deleted = True
        listing.save(update_fields=['is_deleted', 'updated_at'])

    @staticmethod
    def toggle_active(listing: Listing) -> Listing:
        """Flip is_active and return the updated listing."""
        listing.is_active = not listing.is_active
        listing.save(update_fields=['is_active', 'updated_at'])
        return listing
