from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from rest_framework import filters, generics, routers, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.schemas.openapi import AutoSchema

from .models import Cliente, Pedido, Producto, Venta, Vendedor
from .serializers import (
    ClienteSerializer, PedidoSerializer, ProductoSerializer,
    RegistroUsuarioSerializer, VentaSerializer,
)


class ApiFilterBackend(DjangoFilterBackend):
    """Compatibilidad de filtros con el generador OpenAPI de DRF."""

    def get_schema_operation_parameters(self, view):
        return []


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.select_related("vendedor").all()
    serializer_class = ProductoSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (ApiFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ("categoria", "vendedor", "publicado")
    search_fields = ("codigo", "nombre", "descripcion", "categoria")
    ordering_fields = ("nombre", "precio", "stock")


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (ApiFilterBackend, filters.SearchFilter, filters.OrderingFilter)


class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.select_related("producto", "cliente").all()
    serializer_class = VentaSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (ApiFilterBackend, filters.SearchFilter, filters.OrderingFilter)


class VendedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendedor
        fields = ("id", "nombre", "slug", "correo", "activo", "creado_en")
        read_only_fields = ("id", "creado_en")


class VendedorViewSet(viewsets.ModelViewSet):
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (ApiFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("nombre", "slug")
    ordering_fields = ("nombre", "creado_en")


class RegistroUsuarioView(generics.CreateAPIView):
    serializer_class = RegistroUsuarioSerializer
    permission_classes = (AllowAny,)


class PedidoViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (ApiFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    http_method_names = ("get", "post", "head", "options")

    def get_queryset(self):
        return Pedido.objects.filter(usuario=self.request.user).prefetch_related(
            "detalles__producto"
        )

    @action(detail=True, methods=("post",))
    def cancelar(self, request, pk=None):
        with transaction.atomic():
            pedido = self.get_queryset().select_for_update().get(pk=pk)
            if pedido.estado != Pedido.Estado.PENDIENTE_PAGO:
                return Response(
                    {"detail": "Solo se pueden cancelar pedidos pendientes de pago."},
                    status=status.HTTP_409_CONFLICT,
                )
            for detalle in pedido.detalles.select_related("producto").all():
                producto = Producto.objects.select_for_update().get(pk=detalle.producto_id)
                producto.stock += detalle.cantidad
                producto.save(update_fields=("stock",))
            pedido.estado = Pedido.Estado.CANCELADO
            pedido.save(update_fields=("estado", "actualizado_en"))
        return Response(self.get_serializer(pedido).data)


class CatalogoProductoViewSet(viewsets.ReadOnlyModelViewSet):
    """Catálogo público consumible por sitios web y aplicaciones externas."""

    schema = AutoSchema(operation_id_base="CatalogoProducto")
    queryset = Producto.objects.filter(publicado=True).select_related("vendedor")
    serializer_class = ProductoSerializer
    permission_classes = (AllowAny,)
    filter_backends = (ApiFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ("categoria", "vendedor")
    search_fields = ("codigo", "nombre", "descripcion", "categoria")
    ordering_fields = ("nombre", "precio", "stock")
    ordering = ("nombre",)


router = routers.DefaultRouter()
router.register(r"productos", ProductoViewSet)
router.register(r"clientes", ClienteViewSet)
router.register(r"ventas", VentaViewSet)
router.register(r"vendedores", VendedorViewSet)

catalogo_router = routers.DefaultRouter()
catalogo_router.register(r"productos", CatalogoProductoViewSet, basename="catalogo-producto")
pedido_router = routers.DefaultRouter()
pedido_router.register(r"pedidos", PedidoViewSet, basename="pedido")
