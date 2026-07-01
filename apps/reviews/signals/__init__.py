from django.db.models import Avg, Count
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.listings.models import Listing
from apps.reviews.models import Review


def _recalculate_listing_rating(listing_id):
    """Recompute the listing's cached average_rating and reviews_count."""
    aggregates = Review.objects.filter(listing_id=listing_id).aggregate(
        avg_rating=Avg('rating'),
        total=Count('id'),
    )
    Listing.objects.filter(pk=listing_id).update(
        average_rating=aggregates['avg_rating'] or 0,
        reviews_count=aggregates['total'],
    )


@receiver(post_save, sender=Review)
def update_listing_rating_on_save(sender, instance, **kwargs):
    """Recalculate the listing's rating cache after a review is created or updated."""
    _recalculate_listing_rating(instance.listing_id)


@receiver(post_delete, sender=Review)
def update_listing_rating_on_delete(sender, instance, **kwargs):
    """Recalculate the listing's rating cache after a review is removed."""
    _recalculate_listing_rating(instance.listing_id)
