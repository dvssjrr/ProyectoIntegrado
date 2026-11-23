"""
Validadores para la app usuarios.
Validaciones reutilizables.
"""
from django.core.exceptions import ValidationError
import re


def normalizar_rut_chileno(rut_input):
    """Valida un RUT chileno y lo devuelve sin puntos ni guion."""
    rut_limpio = re.sub(r'[.\-\s]', '', str(rut_input or '')).upper()
    if not re.fullmatch(r'\d{7,8}[0-9K]', rut_limpio):
        raise ValidationError('El RUT debe tener formato válido (ej: 12.345.678-9).')

    numero, digito_ingresado = rut_limpio[:-1], rut_limpio[-1]
    suma = sum(int(digit) * (2 + index % 6) for index, digit in enumerate(reversed(numero)))
    digito_calculado = 11 - (suma % 11)
    if digito_calculado == 10:
        digito_calculado = 'K'
    elif digito_calculado == 11:
        digito_calculado = '0'
    else:
        digito_calculado = str(digito_calculado)

    if digito_ingresado != digito_calculado:
        raise ValidationError('El RUT es inválido. Dígito verificador incorrecto.')

    return rut_limpio


def validar_rut_chileno(rut_input):
    """Valida un RUT chileno usando el dígito verificador (Módulo 11)."""
    normalizar_rut_chileno(rut_input)


def validar_nombre_usuario(username):
    """Valida que el nombre de usuario sea válido."""
    if len(username) < 3:
        raise ValidationError('El nombre de usuario debe tener al menos 3 caracteres.')
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError('El nombre de usuario solo puede contener letras, números y guiones bajos.')


def validar_email_corporativo(email):
    """Valida que el email sea corporativo (si es necesario)."""
    # Ejemplo: solo emails de dominio específico
    # Descomenta si necesitas restricción:
    # if not email.endswith('@farmasur.cl'):
    #     raise ValidationError('Solo se permiten emails corporativos.')
    pass
