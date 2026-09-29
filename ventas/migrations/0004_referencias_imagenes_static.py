from django.db import migrations


IMAGENES_POR_CODIGO = {
    "POL-001": "pol-001.png",
    "POL-002": "pol-002.png",
    "POL-003": "pol-003.png",
    "TAZ-001": "taz-001.png",
}


def enlazar_imagenes_static(apps, schema_editor):
    Producto = apps.get_model("ventas", "Producto")
    for codigo, nombre_archivo in IMAGENES_POR_CODIGO.items():
        try:
            producto = Producto.objects.get(codigo=codigo)
        except Producto.DoesNotExist:
            continue

        if producto.imagen:
            continue

        producto.imagen = f"productos/{nombre_archivo}"
        producto.save(update_fields=["imagen"])


def quitar_referencias_static(apps, schema_editor):
    Producto = apps.get_model("ventas", "Producto")
    nombres = [f"productos/{nombre}" for nombre in IMAGENES_POR_CODIGO.values()]
    Producto.objects.filter(imagen__in=nombres).update(imagen="")


class Migration(migrations.Migration):

    dependencies = [
        ("ventas", "0003_imagenes_productos_iniciales"),
    ]

    operations = [
        migrations.RunPython(enlazar_imagenes_static, quitar_referencias_static),
    ]
