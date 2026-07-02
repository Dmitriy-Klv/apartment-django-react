from django.db import models


class ListingPhoto(models.Model):
    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.CASCADE,
        related_name='photos',
    )
    image = models.ImageField(upload_to='listings/')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'listings_listing_photo'
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        """Return a human-readable description of the photo."""
        return f'Photo #{self.id} for listing #{self.listing_id}'
