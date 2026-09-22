from django.db import migrations


PRODUCTOS_INICIALES = [
    {"codigo": "POL-001", "nombre": "Polera Estampada", "precio": 15000, "stock": 20},
    {"codigo": "POL-002", "nombre": "Polera Manga Larga", "precio": 18000, "stock": 15},
    {"codigo": "POL-003", "nombre": "Polerón Estampado", "precio": 25000, "stock": 10},
    {"codigo": "TAZ-001", "nombre": "Tazón Estampado", "precio": 5000, "stock": 30},
]


def cargar_productos(apps, schema_editor):
    Producto = apps.get_model("ventas", "Producto")
    for datos in PRODUCTOS_INICIALES:
        Producto.objects.get_or_create(codigo=datos["codigo"], defaults=datos)


def quitar_productos(apps, schema_editor):
    Producto = apps.get_model("ventas", "Producto")
    codigos = [p["codigo"] for p in PRODUCTOS_INICIALES]
    Producto.objects.filter(codigo__in=codigos).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("ventas", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(cargar_productos, quitar_productos),
    ]
