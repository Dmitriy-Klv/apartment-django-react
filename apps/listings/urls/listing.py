from django.urls import path

from apps.listings.views.listing import ListingDetailView, ListingListCreateView, ListingToggleView, MyListingsView

urlpatterns = [
    path('', ListingListCreateView.as_view(), name='listing-list'),
    path('my/', MyListingsView.as_view(), name='listing-my'),
    path('<int:pk>/', ListingDetailView.as_view(), name='listing-detail'),
    path('<int:pk>/toggle/', ListingToggleView.as_view(), name='listing-toggle'),
]
