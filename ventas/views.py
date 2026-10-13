# ventas/views.py
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date

# Importación de formularios y modelos desde el mismo módulo.
from .forms import ProductoForm, VentaForm
from .models import Cliente, DetalleVenta, Producto, Venta


# ---------- Productos ----------
# Muestra el listado de productos, permite crear, editar y eliminar productos.
def producto_list(request):
    consulta = request.GET.get("q", "").strip()
    productos = Producto.objects.all()
    if consulta:
        productos = productos.filter(
            Q(codigo__icontains=consulta) | Q(nombre__icontains=consulta)
        )
    pagina = Paginator(productos, 9).get_page(request.GET.get("page"))
    return render(
        request,
        "ventas/producto_list.html",
        {"productos": pagina, "consulta": consulta},
    )


# Registra un nuevo producto.
@login_required
def producto_create(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado correctamente.")
            return redirect("producto_list")
    else:
        form = ProductoForm()
    return render(request, "ventas/producto_form.html", {"form": form, "modo": "crear"})


# Edita un producto existente (incluye actualizar el stock).
@login_required
def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect("producto_list")
    else:
        form = ProductoForm(instance=producto)
    return render(request, "ventas/producto_form.html", {"form": form, "modo": "editar", "producto": producto})


# Elimina un producto, previa confirmación.
@login_required
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        producto.delete()
        messages.success(request, "Producto eliminado correctamente.")
        return redirect("producto_list")
    return render(request, "ventas/producto_confirm_delete.html", {"producto": producto})


# ---------- Ventas ----------
# Registra una venta: descuenta stock, guarda el RUT del cliente y, si corresponde, crea o actualiza el registro de cliente habitual.
@login_required
def venta_create(request):
    if request.method == "POST":
        form = VentaForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            producto = datos["producto"]
            cantidad = datos["cantidad"]

            with transaction.atomic():
                # Bloquea el producto para evitar vender más unidades que el stock
                # disponible cuando llegan dos solicitudes simultáneas.
                producto = Producto.objects.select_for_update().get(pk=producto.pk)
                if cantidad > producto.stock:
                    form.add_error(
                        "cantidad",
                        f"Stock insuficiente: quedan {producto.stock} unidades.",
                    )
                    return render(request, "ventas/venta_form.html", {"form": form})
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
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                )
            return redirect("boleta_detail", pk=venta.pk)
    # Si no es POST, se muestra el formulario vacío.
    else:
        form = VentaForm()
    return render(request, "ventas/venta_form.html", {"form": form})


# Historial de ventas registradas y detalle de boleta de venta.
def venta_list(request):
    ventas = Venta.objects.select_related("producto", "cliente").all()
    pagina = Paginator(ventas, 10).get_page(request.GET.get("page"))
    return render(request, "ventas/venta_list.html", {"ventas": pagina})


# Muestra la boleta de una venta recién registrada.
def boleta_detail(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    return render(request, "ventas/boleta_detail.html", {"venta": venta})


@staff_member_required
def reporte_ventas(request):
    """Reporte administrativo de ventas filtrable por rango de fechas."""
    desde = parse_date(request.GET.get("desde", ""))
    hasta = parse_date(request.GET.get("hasta", ""))
    ventas = Venta.objects.select_related("producto").all()
    if desde:
        ventas = ventas.filter(fecha__date__gte=desde)
    if hasta:
        ventas = ventas.filter(fecha__date__lte=hasta)
    return render(
        request,
        "admin/ventas/reporte_ventas.html",
        {
            "desde": desde,
            "hasta": hasta,
            "ventas": ventas,
            "total_ventas": ventas.aggregate(total=Sum("total"))["total"] or 0,
            "cantidad_ventas": ventas.count(),
            "opts": Venta._meta,
            "title": "Reporte de ventas",
        },
    )