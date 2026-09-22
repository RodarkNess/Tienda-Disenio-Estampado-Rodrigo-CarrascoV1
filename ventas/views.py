# ventas/views.py
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

# Importación de formularios y modelos desde el mismo módulo.
from .forms import ProductoForm, VentaForm
from .models import Cliente, Producto, Venta


# ---------- Productos ----------
# Muestra el listado de productos, permite crear, editar y eliminar productos.
def producto_list(request):
    productos = Producto.objects.all()
    return render(request, "ventas/producto_list.html", {"productos": productos})


# Registra un nuevo producto.
def producto_create(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("producto_list")
    else:
        form = ProductoForm()
    return render(request, "ventas/producto_form.html", {"form": form, "modo": "crear"})


# Edita un producto existente (incluye actualizar el stock).
def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect("producto_list")
    else:
        form = ProductoForm(instance=producto)
    return render(request, "ventas/producto_form.html", {"form": form, "modo": "editar", "producto": producto})


# Elimina un producto, previa confirmación.
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        producto.delete()
        return redirect("producto_list")
    return render(request, "ventas/producto_confirm_delete.html", {"producto": producto})


# ---------- Ventas ----------
# Registra una venta: descuenta stock, guarda el RUT del cliente y, si corresponde, crea o actualiza el registro de cliente habitual.
def venta_create(request):
    if request.method == "POST":
        form = VentaForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            producto = datos["producto"]
            cantidad = datos["cantidad"]

            with transaction.atomic():
                cliente = None
                if datos["es_habitual"]:
                    # Se crea o actualiza el cliente habitual usando el RUT como clave.
                    cliente, _ = Cliente.objects.update_or_create(
                        rut=datos["rut_cliente"],
                        defaults={
                            "nombre": datos["nombre_cliente"],
                            "correo": datos["correo_cliente"],
                            "telefono": datos["telefono_cliente"],
                        },
                    )
                # Se descuenta el stock del producto y se guarda la venta.
                producto.stock -= cantidad
                producto.save()
                # Se crea la venta con el RUT del cliente y, si corresponde, el cliente habitual.
                venta = Venta.objects.create(
                    producto=producto,
                    cantidad=cantidad,
                    rut_cliente=datos["rut_cliente"],
                    cliente=cliente,
                    total=producto.precio * cantidad,
                )
            return redirect("boleta_detail", pk=venta.pk)
    # Si no es POST, se muestra el formulario vacío.
    else:
        form = VentaForm()
    return render(request, "ventas/venta_form.html", {"form": form})


# Historial de ventas registradas y detalle de boleta de venta.
def venta_list(request):
    ventas = Venta.objects.select_related("producto", "cliente").all()
    return render(request, "ventas/venta_list.html", {"ventas": ventas})


# Muestra la boleta de una venta recién registrada.
def boleta_detail(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    return render(request, "ventas/boleta_detail.html", {"venta": venta})