# Se importan las librerías necesarias para realizar pruebas unitarias en Django.
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from .models import Pedido, Producto


class CatalogoApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        Producto.objects.all().delete()
        Producto.objects.create(
            codigo="PUB-001",
            nombre="Producto publicado",
            descripcion="Producto para la web externa",
            categoria="poleras",
            precio=15990,
            stock=4,
            publicado=True,
        )
        Producto.objects.create(
            codigo="HID-001",
            nombre="Producto oculto",
            precio=1000,
            stock=2,
            publicado=False,
        )

    def test_catalogo_publico_solo_entrega_productos_publicados(self):
        response = self.client.get("/api/catalogo/productos/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["codigo"], "PUB-001")
        self.assertEqual(response.data["results"][0]["imagen_url"], None)

    def test_catalogo_permite_busqueda_y_filtros(self):
        response = self.client.get(
            "/api/catalogo/productos/",
            {"search": "poleras", "categoria": "poleras"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["codigo"] for item in response.data["results"]], ["PUB-001"])

    def test_api_administrativa_requiere_autenticacion(self):
        response = self.client.get("/api/productos/")

        self.assertEqual(response.status_code, 401)

    def test_esquema_api_esta_disponible(self):
        response = self.client.get("/api/schema/")

        self.assertEqual(response.status_code, 200)

    def test_usuario_puede_registrarse(self):
        response = self.client.post(
            "/api/auth/registro/",
            {"username": "comprador", "email": "buyer@example.com", "password": "segura123"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(username="comprador").exists())

    def test_usuario_puede_obtener_y_refrescar_token_jwt(self):
        User.objects.create_user(username="jwtbuyer", password="segura123")

        login = self.client.post(
            "/api/token/",
            {"username": "jwtbuyer", "password": "segura123"},
            format="json",
        )

        self.assertEqual(login.status_code, 200)
        self.assertIn("access", login.data)
        self.assertIn("refresh", login.data)

        refresh = self.client.post(
            "/api/token/refresh/",
            {"refresh": login.data["refresh"]},
            format="json",
        )

        self.assertEqual(refresh.status_code, 200)
        self.assertIn("access", refresh.data)

    def test_pedido_calcula_total_y_descuenta_stock(self):
        usuario = User.objects.create_user(username="buyer", password="segura123")
        self.client.force_authenticate(usuario)
        producto_id = Producto.objects.get(codigo="PUB-001").id
        response = self.client.post(
            "/api/pedidos/",
            {
                "nombre_destinatario": "Comprador",
                "direccion": "Calle 123",
                "comuna": "Santiago",
                "items": [{"producto_id": producto_id, "cantidad": 2}],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["total"], 31980)
        self.assertEqual(Producto.objects.get(codigo="PUB-001").stock, 2)
        self.assertEqual(Pedido.objects.get().estado, Pedido.Estado.PENDIENTE_PAGO)

    def test_pedido_rechaza_stock_insuficiente_sin_descontar(self):
        usuario = User.objects.create_user(username="buyer2", password="segura123")
        self.client.force_authenticate(usuario)
        producto_id = Producto.objects.get(codigo="PUB-001").id
        response = self.client.post(
            "/api/pedidos/",
            {
                "nombre_destinatario": "Comprador",
                "direccion": "Calle 123",
                "comuna": "Santiago",
                "items": [{"producto_id": producto_id, "cantidad": 99}],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Producto.objects.get(codigo="PUB-001").stock, 4)