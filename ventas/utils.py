# Funciones de apoyo para la app de ventas.
import re

# Deja el RUT solo con números y el dígito verificador, en mayúscula.
def limpiar_rut(rut: str) -> str:
    return re.sub(r"[^0-9kK]", "", rut or "").upper()

# Valida un RUT chileno usando el algoritmo del dígito verificador (módulo 11).
# Retorna True si el RUT es válido, False si no.
def validar_rut(rut: str) -> bool:
    rut = limpiar_rut(rut)
    if len(rut) < 2:
        return False

    cuerpo, dv = rut[:-1], rut[-1]
    if not cuerpo.isdigit():
        return False

    suma = 0
    multiplicador = 2
    # Se recorre el cuerpo del RUT de derecha a izquierda.
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = multiplicador + 1 if multiplicador < 7 else 2

    resto = 11 - (suma % 11)
    if resto == 11:
        dv_esperado = "0"
    elif resto == 10:
        dv_esperado = "K"
    else:
        dv_esperado = str(resto)

    return dv == dv_esperado

# Formatea un RUT chileno validado en el formato estándar con puntos y guión.
def formatear_rut(rut: str) -> str:
    rut = limpiar_rut(rut)
    cuerpo, dv = rut[:-1], rut[-1]
    cuerpo_formateado = ""
    for i, digito in enumerate(reversed(cuerpo)):
        if i and i % 3 == 0:
            cuerpo_formateado = "." + cuerpo_formateado
        cuerpo_formateado = digito + cuerpo_formateado
    return f"{cuerpo_formateado}-{dv}"
