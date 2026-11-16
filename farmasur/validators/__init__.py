"""
Capa de Validadores
Validaciones específicas de negocio reutilizables
"""

from farmasur.validators.usuarios.validators import validar_rut_chileno

__all__ = [
    # Usuarios
    'validar_rut_chileno',
]
