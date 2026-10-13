# Se importan las librerías necesarias para registrar los modelos en el panel de administración de Django
from django.contrib import admin
# Se importan los modelos Cliente, Producto y Venta desde el archivo models.py de la aplicación "ventas"
from .models import Cliente, DetalleVenta, Producto, Venta


@admin.action(description="Marcar productos seleccionados sin stock")
def marcar_sin_stock(modeladmin, request, queryset):
    queryset.update(stock=0)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "precio", "stock", "imagen")
    list_display_links = ("codigo", "nombre")
    search_fields = ("codigo", "nombre")
    list_filter = ("stock",)
    list_editable = ("precio", "stock")
    actions = (marcar_sin_stock,)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("rut", "nombre", "correo", "telefono")
    search_fields = ("rut", "nombre", "correo")
    ordering = ("nombre",)


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("id", "producto", "cantidad", "rut_cliente", "total", "fecha")
    search_fields = ("rut_cliente", "producto__codigo", "producto__nombre")
    list_filter = ("fecha", "cliente")
    date_hierarchy = "fecha"
    list_select_related = ("producto", "cliente")
    readonly_fields = ("total", "fecha")
    inlines = ()

    def save_formset(self, request, form, formset, change):
        instances = formset.save()
        if formset.model is DetalleVenta:
            venta = form.instance
            venta.total = sum(detalle.subtotal for detalle in instances)
            venta.save(update_fields=("total",))


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    fields = ("producto", "cantidad", "precio_unitario", "subtotal")
    readonly_fields = ("subtotal",)


VentaAdmin.inlines = (DetalleVentaInline,)


admin.site.site_header = "Estampados Excelsior"
admin.site.site_title = "Administración | Estampados Excelsior"
admin.site.index_title = "Control de ventas"