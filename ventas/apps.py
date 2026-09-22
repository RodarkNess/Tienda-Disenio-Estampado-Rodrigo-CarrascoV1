# Se importan las librerías necesarias para la configuración de la aplicación "ventas"
from django.apps import AppConfig

# Configuración de la aplicación "ventas"
class VentasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ventas'