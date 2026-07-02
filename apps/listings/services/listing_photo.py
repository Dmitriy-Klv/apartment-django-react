from rest_framework.exceptions import ValidationError

from apps.listings.models import Listing, ListingPhoto

MAX_PHOTOS_PER_LISTING = 5


class ListingPhotoService:

    @staticmethod
    def add_photo(listing: Listing, image) -> ListingPhoto:
        """Attach a new photo to the listing, enforcing the per-listing limit."""
        if listing.photos.count() >= MAX_PHOTOS_PER_LISTING:
            raise ValidationError(f'A listing can have at most {MAX_PHOTOS_PER_LISTING} photos.')

        is_first_photo = not listing.photos.exists()
        return ListingPhoto.objects.create(listing=listing, image=image, is_primary=is_first_photo)

    @staticmethod
    def set_primary(photo: ListingPhoto) -> ListingPhoto:
        """Mark this photo as the listing's cover photo, unsetting any other primary photo."""
        photo.listing.photos.exclude(pk=photo.pk).update(is_primary=False)
        photo.is_primary = True
        photo.save(update_fields=['is_primary'])
        return photo

    @staticmethod
    def delete_photo(photo: ListingPhoto) -> None:
        """Remove a photo, promoting another one to primary if the deleted photo was the cover."""
        listing = photo.listing
        was_primary = photo.is_primary
        photo.delete()

        if was_primary:
            next_photo = listing.photos.first()
            if next_photo:
                next_photo.is_primary = True
                next_photo.save(update_fields=['is_primary'])
