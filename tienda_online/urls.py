# Configuración de URLs para la aplicación de la tienda online.
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from ventas import views

# Configuración de URLs para la aplicación de la tienda online.
urlpatterns = [
    path("admin/reportes/ventas/", views.reporte_ventas, name="admin_reporte_ventas"),
    path("admin/", admin.site.urls),
    path("", include("ventas.urls")),
]

# Se agrega la configuración para servir archivos de medios (imágenes) durante el desarrollo.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)