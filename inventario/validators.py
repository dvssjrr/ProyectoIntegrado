"""
Validadores para la app inventario.
Validaciones reutilizables.
"""
from django.core.exceptions import ValidationError
from datetime import date


def validar_fecha_vencimiento(fecha):
    """Valida que la fecha de vencimiento sea válida y en el futuro."""
    if fecha < date.today():
        raise ValidationError('La fecha de vencimiento no puede ser en el pasado.')


def validar_cantidad_positiva(cantidad):
    """Valida que la cantidad sea positiva."""
    if cantidad <= 0:
        raise ValidationError('La cantidad debe ser mayor que 0.')


def validar_numero_lote(numero_lote):
    """Valida formato del número de lote."""
    # Puede ser LOTE-AAAA-NNN o similar
    # Ajusta según regla de negocio
    if not numero_lote or len(numero_lote) < 3:
        raise ValidationError('El número de lote es inválido.')


def validar_precio_positivo(precio):
    """Valida que el precio sea positivo."""
    if precio <= 0:
        raise ValidationError('El precio debe ser mayor que 0.')
