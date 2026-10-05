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

## Notas técnicas
- El RUT se valida con el algoritmo del dígito verificador chileno
  (`ventas/utils.py`).
- Las imágenes de producto se guardan con `Pillow` (paquete externo) en
  `media/productos/`; si un producto no tiene imagen se muestra un
  placeholder.
- Interfaz hecha con Tailwind CSS (CDN), tema oscuro con acentos neon.