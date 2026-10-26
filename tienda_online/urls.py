# Configuración de URLs para la aplicación de la tienda online.
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from ventas import views
from ventas.api import router

# Configuración de URLs para la aplicación de la tienda online.
urlpatterns = [
    path("admin/reportes/ventas/", views.reporte_ventas, name="admin_reporte_ventas"),
    path("admin/", admin.site.urls),
    path("", include("ventas.urls")),
    path("api-auth/", include("rest_framework.urls")),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
]

# Se agrega la configuración para servir archivos de medios (imágenes) durante el desarrollo.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)