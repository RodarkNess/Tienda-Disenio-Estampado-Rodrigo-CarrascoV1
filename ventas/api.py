 #Importamos routers y viewsets de Django Rest Framework
from rest_framework import routers, viewsets
#Importamos los modelos Venta, Producto y Cliente desde el archivo models.py
from .models import Venta, Producto, Cliente
#Importamos los serializadores VentaSerializer, ProductoSerializer y ClienteSerializer desde el archivo serializers.py
from .serializers import VentaSerializer, ProductoSerializer, ClienteSerializer

# Creamos un viewset para el modelo Producto, que permite realizar operaciones CRUD (crear, leer, actualizar y eliminar) sobre los productos.
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

# Creamos un viewset para el modelo Cliente, que permite realizar operaciones CRUD (crear, leer, actualizar y eliminar) sobre los clientes.
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

# Creamos un viewset para el modelo Venta, que permite realizar operaciones CRUD (crear, leer, actualizar y eliminar) sobre las ventas.
class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

# Creamos un router para registrar los viewsets de Producto, Cliente y Venta,
# lo que permite generar automáticamente las URLs correspondientes para acceder a las operaciones CRUD de cada modelo.
router = routers.DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'ventas', VentaViewSet)