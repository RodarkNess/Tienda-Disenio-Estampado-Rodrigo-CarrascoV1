#Import serializers from Django REST Framework to handle serialization of model instances into JSON format and vice versa.
from rest_framework import serializers
from .models import Venta, Producto, Cliente

# Define serializers for the Producto, Cliente, and Venta models to convert model instances to JSON format and validate incoming data.
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['__all__']

# Define a serializer for the Cliente model.
class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['__all__']

# Define a serializer for the Venta model, which includes nested serializers for the related Producto and Cliente models.
class VentaSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    cliente = ClienteSerializer(read_only=True)

    class Meta:
        model = Venta
        fields = ['__all__']