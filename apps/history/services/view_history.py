from apps.history.models import ViewHistory


class ViewHistoryService:

    @staticmethod
    def record_view(listing, user=None) -> None:
        """Record a listing page view for an authenticated or anonymous user."""
        ViewHistory.objects.create(listing=listing, user=user)
