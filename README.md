# Tienda Online — Caso 2: Control de Venta Básico

Proyecto Django para TI3041 — Programación Backend (Evaluación Sumativa 1).

## Requisitos
- Python 3.11+
- pip

## Instalación

```bash
where python
python -m venv .venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
pip install python-dotenv psycopg2

```Si no hay Superuser utilizar:
python manage.py createsuperuser

```

En Vercel configura las mismas credenciales usando `DB_HOST`, `DB_PORT`,
`DB_NAME`, `DB_USER` y `DB_PASSWORD`. Usa la cadena de conexión **Transaction
Pooler** de Supabase (puerto `6543`) y la contraseña actual de la base de
datos; no uses la contraseña del usuario de la cuenta de Supabase.

Vercel define automáticamente `VERCEL_URL`, `VERCEL_BRANCH_URL` y
`VERCEL_PROJECT_PRODUCTION_URL`. Django las utiliza para aceptar tanto la URL
de producción como las URLs de preview, por lo que no es necesario copiar una
URL concreta de Vercel en `ALLOWED_HOSTS`. Después de cambiar esta
configuración hay que crear un nuevo deployment en Vercel.

Este código se utiliza para subir la colección de archivos multimedia
python manage.py collectstatic

python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Luego abre http://127.0.0.1:8000/

Al migrar se cargan automáticamente 4 productos de ejemplo:
Polera Estampada, Polera Manga Larga, Polerón Estampado y Tazón Estampado.

## Funcionalidad
- **/** — Listado de productos (catálogo).
- **/productos/nuevo/** — Registrar producto (nombre, código, cantidad, precio, imagen opcional).
- **/productos/<id>/editar/** — Editar producto / actualizar stock.
- **/productos/<id>/eliminar/** — Eliminar producto.
- **/ventas/nueva/** — Registrar venta: elige producto, cantidad y RUT del cliente.
  Si la persona marca "cliente habitual" se piden además nombre, correo y
  teléfono, y quedan guardados para próximas compras. Si no, solo se
  guarda el RUT para la boleta.
- **/ventas/** — Historial de ventas.
- **/ventas/<id>/boleta/** — Boleta de una venta puntual.
- **/admin/reportes/ventas/** — Reporte administrativo por rango de fechas (requiere
  usuario staff).

## API para frontend externo

El backend conserva la interfaz Django existente y además expone una API REST
para que otro repositorio pueda construir el frontend público:

- **GET `/api/catalogo/productos/`** — Catálogo público paginado. Solo entrega
  productos marcados como publicados.
- **GET `/api/catalogo/productos/<id>/`** — Detalle público de un producto.
- **GET `/api/schema/`** — Esquema de la API.
- **`/api/productos/`, `/api/clientes/`, `/api/ventas/` y `/api/vendedores/`** —
  Operaciones administrativas protegidas con JWT.
- **POST `/api/auth/registro/`** — Crear una cuenta de comprador.
- **`/api/pedidos/`** — Crear y consultar pedidos del comprador autenticado.
- **POST `/api/pedidos/<id>/cancelar/`** — Cancelar un pedido pendiente y
  devolver sus unidades al stock.
- **`/api/token/` y `/api/token/refresh/`** — Obtener y renovar tokens JWT.

El catálogo acepta `search`, `categoria`, `vendedor`, `ordering` y `page`.
Las respuestas son paginadas con 20 elementos por página e incluyen
`imagen_url` absoluta cuando el producto tiene imagen.

### Despliegue público

- API REST: https://tienda-estampado-api-rodrigo-carras.vercel.app/
- Frontend consumidor: https://multiversal-nerd.vercel.app/

El frontend usa `POST /api/token/` para autenticarse y envía el token como
`Authorization: Bearer <access_token>` en las operaciones protegidas.

Para permitir que el frontend se conecte desde otro dominio, define
`CORS_ALLOWED_ORIGINS` como una lista separada por comas, por ejemplo:

```text
CORS_ALLOWED_ORIGINS=https://mi-frontend.example.com,http://localhost:3000
```

Los campos `descripcion`, `categoria`, `publicado` y `vendedor` preparan el
catálogo para incorporar múltiples vendedores sin afectar los productos
existentes. Los productos antiguos quedan publicados y sin vendedor hasta que
se asignen desde el panel administrativo.

### Pedidos y stock

Para crear un pedido, el frontend debe autenticarse con JWT y enviar:

```json
{
  "nombre_destinatario": "Juan Pérez",
  "direccion": "Av. Principal 123",
  "comuna": "Santiago",
  "telefono": "+56 9 1234 5678",
  "items": [
    {"producto_id": 1, "cantidad": 2}
  ]
}
```

El backend consulta nuevamente los precios, valida que los productos estén
publicados, bloquea las filas de inventario dentro de una transacción,
descuenta el stock y calcula el total. El precio y total enviados por el
frontend no son aceptados como fuente de verdad.

Los pedidos se crean inicialmente con estado `pendiente_pago`. La cancelación
solo está permitida en ese estado y repone el stock. La integración con un
proveedor de pagos debe confirmar el pago mediante un webhook/backend antes de
cambiar el pedido a `pagado`; todavía no se simula una aprobación de pago.

## Notas técnicas
- El RUT se valida con el algoritmo del dígito verificador chileno
  (`ventas/utils.py`).
- Las imágenes de producto se guardan con `Pillow` (paquete externo) en
  `media/productos/`; si un producto no tiene imagen se muestra un
  placeholder.
- Interfaz hecha con Tailwind CSS (CDN), tema oscuro con acentos neon.
- El catálogo incluye búsqueda por nombre/código, tarjetas visuales para
  poleras y paginación.
- Las operaciones que modifican productos o registran ventas requieren iniciar
  sesión mediante `/admin/login/`. El panel Admin incluye búsquedas, filtros,
  acción para marcar productos sin stock, detalle de venta como inline y
  cálculo del total.
- En local se usa SQLite si no existen `DB_HOST` y `DB_NAME`. En Supabase o
  cualquier PostgreSQL administrado se activan automáticamente las variables
  `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` y `DB_SSLMODE`.
- Para producción, ejecuta `python manage.py collectstatic --noinput` y
  configura `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, `ALLOWED_HOSTS` y las
  variables de base de datos en el proveedor. WhiteNoise sirve los estáticos
  recolectados.