from django.urls import path

from apps.reviews.views.review import ListingReviewsView, ReviewCreateView, ReviewDetailView

urlpatterns = [
    path('reviews/', ReviewCreateView.as_view(), name='review-create'),
    path('reviews/<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
    path('listings/<int:listing_id>/reviews/', ListingReviewsView.as_view(), name='listing-reviews'),
]
