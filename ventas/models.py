# Django modelo de datos para la app de ventas.
from django.contrib.staticfiles import finders
from django.contrib.auth.models import User
from django.db import models
from django.templatetags.static import static


class Vendedor(models.Model):
    """Comerciante que publica productos en la plataforma."""
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil_vendedor",
        null=True,
        blank=True,
    )
    nombre = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    correo = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


# Modelo para representar un producto disponible para la venta en la tienda.
class Producto(models.Model):
    """Producto disponible para la venta en la tienda."""
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(max_length=80, blank=True)
    precio = models.PositiveIntegerField(help_text="Precio en pesos chilenos (CLP)")
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)
    vendedor = models.ForeignKey(
        Vendedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos",
    )
    publicado = models.BooleanField(default=True)

    # La fecha de creación se guarda automáticamente al crear el registro.
    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    @property
    def imagen_url(self):
        if not self.imagen:
            return ""

        if finders.find(self.imagen.name):
            return static(self.imagen.name)

        return self.imagen.url

# Modelo para representar un cliente habitual de la tienda.
# Solo se crea un registro aquí cuando la persona acepta ser cliente habitual al momento de comprar; si no, la venta solo guarda su RUT.
class Cliente(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cliente",
        null=True,
        blank=True,
    )
    rut = models.CharField(max_length=12, unique=True, verbose_name="RUT")
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)

    # La fecha de creación se guarda automáticamente al crear el registro.
    class Meta:
        ordering = ["nombre"]
    
    def __str__(self):
        return f"{self.nombre} - {self.rut}"

# Boleta o registro de una venta de un producto a un cliente identificado por su RUT.
class Venta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="ventas")
    cantidad = models.PositiveIntegerField()
    rut_cliente = models.CharField(max_length=12, verbose_name="RUT del cliente")
    # Se enlaza solo si la persona quiso ser cliente habitual; si no, queda en null.
    cliente = models.ForeignKey(
        Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name="ventas"
    )
    total = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    # Se guarda el correo del cliente al momento de la venta, para poder enviarle la boleta aunque no sea cliente habitual.
    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Venta #{self.pk} - {self.producto.nombre} x{self.cantidad}"


class DetalleVenta(models.Model):
    """Detalle editable de una venta, administrable como inline."""
    venta = models.ForeignKey(
        Venta, on_delete=models.CASCADE, related_name="detalles"
    )
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.PositiveIntegerField(
        help_text="Precio congelado al momento de la venta (CLP)"
    )

    class Meta:
        verbose_name = "detalle de venta"
        verbose_name_plural = "detalles de venta"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"


class Pedido(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE_PAGO = "pendiente_pago", "Pendiente de pago"
        PAGADO = "pagado", "Pagado"
        PREPARANDO = "preparando", "Preparando"
        ENVIADO = "enviado", "Enviado"
        ENTREGADO = "entregado", "Entregado"
        CANCELADO = "cancelado", "Cancelado"

    usuario = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="pedidos"
    )
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE_PAGO
    )
    total = models.PositiveIntegerField(default=0)
    nombre_destinatario = models.CharField(max_length=120)
    direccion = models.CharField(max_length=255)
    comuna = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"Pedido #{self.pk} - {self.usuario.username}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    vendedor = models.ForeignKey(
        Vendedor, on_delete=models.SET_NULL, null=True, blank=True
    )
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario