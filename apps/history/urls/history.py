from django.urls import path

from apps.history.views.history import PopularListingsView, PopularSearchesView

urlpatterns = [
    path('searches/popular/', PopularSearchesView.as_view(), name='popular-searches'),
    path('listings/popular/', PopularListingsView.as_view(), name='popular-listings'),
]
