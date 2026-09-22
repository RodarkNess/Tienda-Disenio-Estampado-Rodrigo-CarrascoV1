# Configuración de URLs para la aplicación de la tienda online.
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, path

# Configuración de URLs para la aplicación de la tienda online.
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("ventas.urls")),
]

# Se agrega la configuración para servir archivos de medios (imágenes) durante el desarrollo.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)