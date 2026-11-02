from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction

from .models import Cliente, DetallePedido, Pedido, Producto, Venta

# Define serializers for the Producto, Cliente, and Venta models to convert model instances to JSON format and validate incoming data.
class ProductoSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = (
            "id", "codigo", "nombre", "descripcion", "categoria", "precio",
            "stock", "imagen", "imagen_url", "vendedor", "publicado",
        )
        read_only_fields = ("id", "imagen_url")

    def get_imagen_url(self, obj):
        if not obj.imagen:
            return None
        request = self.context.get("request")
        url = obj.imagen_url
        return request.build_absolute_uri(url) if request else url

# Define a serializer for the Cliente model.
class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ("id", "rut", "nombre", "correo", "telefono")

# Define a serializer for the Venta model, which includes nested serializers for the related Producto and Cliente models.
class VentaSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    cliente = ClienteSerializer(read_only=True)

    class Meta:
        model = Venta
        fields = (
            "id", "producto", "cantidad", "rut_cliente", "cliente", "total", "fecha",
        )


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("username", "email", "password", "first_name", "last_name")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class DetallePedidoSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    subtotal = serializers.IntegerField(read_only=True)

    class Meta:
        model = DetallePedido
        fields = ("id", "producto", "cantidad", "precio_unitario", "subtotal")


class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    items = serializers.ListField(
        write_only=True, child=serializers.DictField(), required=True
    )

    class Meta:
        model = Pedido
        fields = (
            "id", "estado", "total", "nombre_destinatario", "direccion",
            "comuna", "telefono", "creado_en", "actualizado_en", "detalles", "items",
        )
        read_only_fields = (
            "id", "estado", "total", "creado_en", "actualizado_en", "detalles",
        )

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError(
                "El pedido debe contener al menos un producto."
            )
        for item in items:
            if not isinstance(item.get("producto_id"), int) or item["producto_id"] <= 0:
                raise serializers.ValidationError("Cada producto_id debe ser válido.")
            if not isinstance(item.get("cantidad"), int) or item["cantidad"] <= 0:
                raise serializers.ValidationError("Cada cantidad debe ser positiva.")
        return items

    def create(self, validated_data):
        items = validated_data.pop("items")
        with transaction.atomic():
            pedido = Pedido.objects.create(
                usuario=self.context["request"].user, **validated_data
            )
            total = 0
            for item in items:
                try:
                    producto = Producto.objects.select_for_update().get(
                        pk=item["producto_id"], publicado=True
                    )
                except Producto.DoesNotExist as exc:
                    raise serializers.ValidationError(
                        "Uno de los productos no está publicado o no existe."
                    ) from exc
                cantidad = item["cantidad"]
                if cantidad > producto.stock:
                    raise serializers.ValidationError(
                        f"Stock insuficiente para {producto.nombre}."
                    )
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    vendedor=producto.vendedor,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                )
                producto.stock -= cantidad
                producto.save(update_fields=("stock",))
                total += producto.precio * cantidad
            pedido.total = total
            pedido.save(update_fields=("total",))
        return pedido