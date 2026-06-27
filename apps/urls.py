from django.urls import include, path

urlpatterns = [
    path('auth/', include('apps.users.urls.user')),
    path('listings/', include('apps.listings.urls.listing')),
    path('bookings/', include('apps.bookings.urls.booking')),
    path('reviews/', include('apps.reviews.urls.review')),
    path('history/', include('apps.history.urls.history')),
]
