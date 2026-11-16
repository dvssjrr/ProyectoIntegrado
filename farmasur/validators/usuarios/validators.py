"""
Validadores para la app usuarios.
Validaciones reutilizables.
"""
from django.core.exceptions import ValidationError
import re


def validar_rut_chileno(rut_input):
    """
    Valida un RUT chileno usando el dígito verificador (Módulo 11).
    
    Acepta formatos:
    - 12345678-9
    - 12.345.678-9
    
    Lanza ValidationError si es inválido.
    """
    # Limpiar espacios
    rut = rut_input.strip()
    
    # Permitir formato con puntos y guión
    if '.' in rut or '-' in rut:
        rut_limpio = rut.replace('.', '').replace('-', '')
    else:
        rut_limpio = rut
    
    # Validar que sea numérico + un carácter
    if not re.match(r'^\d{7,8}[0-9K]$', rut_limpio):
        raise ValidationError('El RUT debe tener formato válido (ej: 12.345.678-9).')
    
    # Separar número y dígito verificador
    num_rut = rut_limpio[:-1]
    digito_ingresado = rut_limpio[-1].upper()
    
    # Calcular dígito verificador usando Módulo 11
    suma = 0
    multiplicador = 2
    
    for digit in reversed(num_rut):
        suma += int(digit) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2
    
    residuo = suma % 11
    digito_calculado = 11 - residuo
    
    if digito_calculado == 10:
        digito_calculado = 'K'
    elif digito_calculado == 11:
        digito_calculado = '0'
    else:
        digito_calculado = str(digito_calculado)
    
    if digito_ingresado != digito_calculado:
        raise ValidationError(f'El RUT es inválido. Dígito verificador incorrecto.')


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
