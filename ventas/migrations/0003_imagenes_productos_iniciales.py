from pathlib import Path

from django.core.files import File
from django.db import migrations

# Las fotos viven junto al codigo de la app (no en MEDIA_ROOT), asi quedan
# versionadas con el proyecto y esta migracion las copia a MEDIA_ROOT/productos/
# la primera vez que alguien corre `migrate`.
SEED_IMAGES_DIR = Path(__file__).resolve().parent.parent / "seed_images"

IMAGENES_POR_CODIGO = {
    "POL-001": "pol-001.png",
    "POL-002": "pol-002.png",
    "POL-003": "pol-003.png",
    "TAZ-001": "taz-001.png",
}


def cargar_imagenes(apps, schema_editor):
    Producto = apps.get_model("ventas", "Producto")
    for codigo, nombre_archivo in IMAGENES_POR_CODIGO.items():
        try:
            producto = Producto.objects.get(codigo=codigo)
        except Producto.DoesNotExist:
            continue

        # No pisar una imagen si ya tiene una (por ejemplo, subida a mano).
        if producto.imagen:
            continue

        ruta_origen = SEED_IMAGES_DIR / nombre_archivo
        if not ruta_origen.exists():
            continue

        with open(ruta_origen, "rb") as archivo:
            producto.imagen.save(nombre_archivo, File(archivo), save=True)


def quitar_imagenes(apps, schema_editor):
    Producto = apps.get_model("ventas", "Producto")
    Producto.objects.filter(codigo__in=IMAGENES_POR_CODIGO.keys()).update(imagen="")


class Migration(migrations.Migration):

    dependencies = [
        ("ventas", "0002_productos_iniciales"),
    ]

    operations = [
        migrations.RunPython(cargar_imagenes, quitar_imagenes),
    ]
