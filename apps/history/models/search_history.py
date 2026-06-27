from django.conf import settings
from django.db import models


class SearchHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_history',
    )
    keyword = models.CharField(max_length=255)
    count = models.PositiveIntegerField(default=1)
    last_searched = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'history_search'
        ordering = ['-count', '-last_searched']
        unique_together = ('user', 'keyword')

    def __str__(self):
        return f'{self.user} — "{self.keyword}" ({self.count}x)'
