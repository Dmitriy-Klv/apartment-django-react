from django.conf import settings
from django.db import models


class ViewHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='view_history',
        null=True,
        blank=True,
    )
    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.CASCADE,
        related_name='view_history',
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'history_view'
        ordering = ['-viewed_at']

    def __str__(self):
        return f'{self.user} → {self.listing} at {self.viewed_at}'
