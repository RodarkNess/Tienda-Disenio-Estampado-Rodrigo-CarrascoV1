# Se importan las librerías necesarias para registrar los modelos en el panel de administración de Django
from django.contrib import admin
# Se importan los modelos Cliente, Producto y Venta desde el archivo models.py de la aplicación "ventas"
from django import forms
from .models import Cliente, DetalleVenta, Producto, Venta
from .utils import formatear_rut, validar_rut


@admin.action(description="Marcar productos seleccionados sin stock") # Se define una acción personalizada para marcar los productos seleccionados como sin stock
def marcar_sin_stock(modeladmin, request, queryset):
    queryset.update(stock=0)


@admin.register(Producto) # Se registra el modelo Producto en el panel de administración de Django
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "precio", "stock", "imagen")
    list_display_links = ("codigo", "nombre")
    search_fields = ("codigo", "nombre")
    list_filter = ("stock",)
    list_editable = ("precio", "stock")
    list_per_page = 12
    empty_value_display = "—"
    actions = (marcar_sin_stock,)


@admin.register(Cliente) # Se registra el modelo Cliente en el panel de administración de Django
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("rut", "nombre", "correo", "telefono")
    # El prefijo "=" exige coincidencia exacta del RUT, incluidos puntos y guión.
    search_fields = ("=rut", "nombre", "correo", "telefono")
    ordering = ("nombre",)
    list_per_page = 12

    class form(forms.ModelForm):
        class Meta:
            model = Cliente
            fields = "__all__"

        def clean_rut(self):
            rut = self.cleaned_data["rut"]
            if not validar_rut(rut):
                raise forms.ValidationError("El RUT ingresado no es válido.")
            rut_formateado = formatear_rut(rut)
            if rut != rut_formateado:
                raise forms.ValidationError(
                    "Ingresa el RUT con puntos y guión, por ejemplo: 12.345.678-9."
                )
            return rut_formateado


@admin.register(Venta) # Se registra el modelo Venta en el panel de administración de Django
class VentaAdmin(admin.ModelAdmin): # Se define una clase para personalizar la visualización del modelo Venta en el panel de administración de Django
    list_display = ("id", "producto", "cantidad", "rut_cliente", "total", "fecha")
    search_fields = ("rut_cliente", "producto__codigo", "producto__nombre")
    list_filter = ("fecha", "cliente")
    date_hierarchy = "fecha"
    list_select_related = ("producto", "cliente")
    readonly_fields = ("total", "fecha")
    list_per_page = 12
    save_as = True
    inlines = ()

    def save_formset(self, request, form, formset, change): # Se sobrescribe el método save_formset para calcular el total de la venta al guardar los detalles de la venta
        instances = formset.save()
        if formset.model is DetalleVenta:
            venta = form.instance
            venta.total = sum(detalle.subtotal for detalle in instances)
            venta.save(update_fields=("total",))


class DetalleVentaInline(admin.TabularInline): # Se define una clase inline para mostrar los detalles de la venta en el panel de administración
    model = DetalleVenta
    extra = 1
    fields = ("producto", "cantidad", "precio_unitario", "subtotal")
    readonly_fields = ("subtotal",)


VentaAdmin.inlines = (DetalleVentaInline,) # Se asigna la clase inline DetalleVentaInline al modelo VentaAdmin para mostrar los detalles de la venta en el panel de administración


admin.site.site_header = "Estampados Excelsior" # Se personaliza el encabezado del panel de administración de Django
admin.site.site_title = "Administración | Estampados Excelsior" # Se personaliza el título del panel de administración de Django
admin.site.index_title = "Control de ventas" # Se personaliza el título de la página de inicio del panel de administración de Django