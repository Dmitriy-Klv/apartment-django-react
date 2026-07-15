from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser

SCHEMA_ACCESS = {
    'authentication_classes': [SessionAuthentication],
    'permission_classes': [IsAdminUser],
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.urls')),
    path('api/schema/', SpectacularAPIView.as_view(**SCHEMA_ACCESS), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema', **SCHEMA_ACCESS), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema', **SCHEMA_ACCESS), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
