from django.contrib import admin

from apps.history.models import SearchHistory, ViewHistory


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for SearchHistory model."""

    list_display = ['keyword', 'user', 'count']
    search_fields = ['keyword', 'user__email']


@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for ViewHistory model."""

    list_display = ['listing', 'user', 'viewed_at']
    search_fields = ['listing__title', 'user__email']
