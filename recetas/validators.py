"""
Validadores para la app recetas.
Validaciones reutilizables.
"""
from django.core.exceptions import ValidationError
from datetime import date


def validar_folio_receta(folio):
    """Valida que el folio tenga formato válido."""
    if not folio or len(folio) < 5:
        raise ValidationError('El folio debe tener al menos 5 caracteres.')


def validar_rut_paciente(rut):
    """Valida RUT del paciente (formato básico)."""
    if not rut or len(rut) < 7:
        raise ValidationError('El RUT del paciente no es válido.')


def validar_fecha_emision_receta(fecha):
    """Valida que la fecha de emisión sea válida y no sea futura."""
    if fecha > date.today():
        raise ValidationError('La fecha de emisión no puede ser futura.')


def validar_medicamentos_receta(medicamentos):
    """Valida estructura de medicamentos."""
    if not isinstance(medicamentos, list) or len(medicamentos) == 0:
        raise ValidationError('Debe incluir al menos un medicamento.')
    
    for med in medicamentos:
        if not isinstance(med, dict):
            raise ValidationError('Cada medicamento debe ser un objeto.')
        if 'sku' not in med or 'cantidad' not in med:
            raise ValidationError('Cada medicamento debe tener sku y cantidad.')
