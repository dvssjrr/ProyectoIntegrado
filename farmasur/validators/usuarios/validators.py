"""
Validadores para la app usuarios.
Validaciones reutilizables.
"""
from django.core.exceptions import ValidationError
import re


def validar_rut_chileno(rut_input):
    """
    Valida el formato de un RUT chileno.
    
    Acepta formatos:
    - 12345678-9
    - 12.345.678-9
    
    Lanza ValidationError si es inválido.
    """
    rut_limpio = rut_input.strip().replace('.', '').replace('-', '').upper()

    if not re.fullmatch(r'\d{7,8}[0-9K]', rut_limpio):
        raise ValidationError('El RUT debe tener formato válido (ej: 12.345.678-9).')


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
