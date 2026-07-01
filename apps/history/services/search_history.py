from django.db.models import F

from apps.history.models import SearchHistory


class SearchHistoryService:

    @staticmethod
    def record_search(user, keyword: str) -> None:
        """Create or atomically increment the search count for an authenticated user."""
        keyword = keyword.strip()[:255]
        if not keyword:
            return
        obj, created = SearchHistory.objects.get_or_create(
            user=user,
            keyword=keyword,
            defaults={'count': 1},
        )
        if not created:
            SearchHistory.objects.filter(pk=obj.pk).update(count=F('count') + 1)
