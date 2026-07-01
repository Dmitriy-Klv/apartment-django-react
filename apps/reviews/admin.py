from django.contrib import admin

from apps.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin configuration for Review model."""

    list_display = ['listing', 'author', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['listing__title', 'author__email', 'comment']
    readonly_fields = ['created_at']
