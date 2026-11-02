# Configuración de URLs para la aplicación de la tienda online.
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import AllowAny
from rest_framework.schemas import get_schema_view
from ventas import views
from ventas.api import RegistroUsuarioView, catalogo_router, pedido_router, router

# Configuración de URLs para la aplicación de la tienda online.
urlpatterns = [
    path("admin/reportes/ventas/", views.reporte_ventas, name="admin_reporte_ventas"),
    path("admin/", admin.site.urls),
    path("", include("ventas.urls")),
    path("api-auth/", include("rest_framework.urls")),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/auth/registro/", RegistroUsuarioView.as_view(), name="api-registro"),
    path('api/', include(router.urls)),
    path("api/catalogo/", include(catalogo_router.urls)),
    path("api/", include(pedido_router.urls)),
    path(
        "api/schema/",
        get_schema_view(
            title="API Tienda de Estampados",
            description="Catálogo y operaciones de la plataforma.",
            version="1.0.0",
            public=True,
            permission_classes=(AllowAny,),
        ),
        name="api-schema",
    ),
]

# Se agrega la configuración para servir archivos de medios (imágenes) durante el desarrollo.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)