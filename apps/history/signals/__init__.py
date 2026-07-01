from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.history.models import ViewHistory
from apps.listings.models import Listing


@receiver(post_save, sender=ViewHistory)
def increment_listing_views_count(sender, instance, created, **kwargs):
    """Increment the listing's cached views_count when a view is logged."""
    if created:
        Listing.objects.filter(pk=instance.listing_id).update(views_count=F('views_count') + 1)
