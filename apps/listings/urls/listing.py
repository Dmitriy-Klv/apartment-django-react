from django.urls import path

from apps.listings.views.listing import ListingDetailView, ListingListCreateView, ListingToggleView, MyListingsView
from apps.listings.views.listing_photo import ListingPhotoDetailView, ListingPhotoListCreateView

urlpatterns = [
    path('', ListingListCreateView.as_view(), name='listing-list'),
    path('my/', MyListingsView.as_view(), name='listing-my'),
    path('<int:pk>/', ListingDetailView.as_view(), name='listing-detail'),
    path('<int:pk>/toggle/', ListingToggleView.as_view(), name='listing-toggle'),
    path('<int:pk>/photos/', ListingPhotoListCreateView.as_view(), name='listing-photo-list'),
    path('<int:pk>/photos/<int:photo_id>/', ListingPhotoDetailView.as_view(), name='listing-photo-detail'),
]
