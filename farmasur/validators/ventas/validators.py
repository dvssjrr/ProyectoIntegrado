"""
Validadores para la app ventas.
Validaciones reutilizables.
"""
from django.core.exceptions import ValidationError


def validar_monto_positivo(monto):
    """Valida que el monto sea positivo."""
    if monto <= 0:
        raise ValidationError('El monto debe ser mayor que 0.')


def validar_porcentaje_descuento(porcentaje):
    """Valida que el porcentaje esté entre 0 y 100."""
    if porcentaje < 0 or porcentaje > 100:
        raise ValidationError('El porcentaje debe estar entre 0 y 100.')


def validar_folio_venta(folio):
    """Valida que el folio tenga formato válido."""
    if not folio or len(folio) < 5:
        raise ValidationError('El folio debe tener al menos 5 caracteres.')


def validar_items_venta(items):
    """Valida estructura de items de venta."""
    if not isinstance(items, list) or len(items) == 0:
        raise ValidationError('Debe incluir al menos un artículo en la venta.')
    
    for item in items:
        if not isinstance(item, dict):
            raise ValidationError('Cada artículo debe ser un objeto.')
        if 'sku' not in item or 'cantidad' not in item or 'precio_unitario' not in item:
            raise ValidationError('Cada artículo debe tener sku, cantidad y precio_unitario.')
