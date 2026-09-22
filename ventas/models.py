# Django modelo de datos para la app de ventas.
from django.db import models

# Modelo para representar un producto disponible para la venta en la tienda.
class Producto(models.Model):
    """Producto disponible para la venta en la tienda."""
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    nombre = models.CharField(max_length=100)
    precio = models.PositiveIntegerField(help_text="Precio en pesos chilenos (CLP)")
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)

    # La fecha de creación se guarda automáticamente al crear el registro.
    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

# Modelo para representar un cliente habitual de la tienda.
# Solo se crea un registro aquí cuando la persona acepta ser cliente habitual al momento de comprar; si no, la venta solo guarda su RUT.
class Cliente(models.Model):
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