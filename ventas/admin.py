# Se importan las librerías necesarias para registrar los modelos en el panel de administración de Django
from django.contrib import admin
# Se importan los modelos Cliente, Producto y Venta desde el archivo models.py de la aplicación "ventas"
from .models import Cliente, Producto, Venta

# Se registran los modelos Cliente, Producto y Venta en el panel de administración de Django
admin.site.register(Producto)
admin.site.register(Cliente)
admin.site.register(Venta)