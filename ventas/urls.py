# Django configuración de URL para la app de ventas.
from django.urls import path
from . import views

# patrones de URL para las vistas de productos y ventas.
urlpatterns = [
    path("", views.producto_list, name="producto_list"),
    path("productos/nuevo/", views.producto_create, name="producto_create"),
    path("productos/<int:pk>/editar/", views.producto_update, name="producto_update"),
    path("productos/<int:pk>/eliminar/", views.producto_delete, name="producto_delete"),
    path("ventas/nueva/", views.venta_create, name="venta_create"),
    path("ventas/", views.venta_list, name="venta_list"),
    path("ventas/<int:pk>/boleta/", views.boleta_detail, name="boleta_detail"),
]