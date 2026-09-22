#!/usr/bin/env python
# Línea de comandos de Django para tareas administrativas
import os
import sys

# función main que se ejecuta al iniciar el script
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_online.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Estás seguro de que está instalado y "
            "disponible en tu variable de entorno PYTHONPATH? ¿Olvidaste "
            "activar un entorno virtual?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()