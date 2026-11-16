"""
Capa de Validadores
Validaciones específicas de negocio reutilizables
"""

from farmasur.validators.usuarios.validators import (
    validar_rut,
    validar_email,
    validar_contrasena,
)
from farmasur.validators.inventario.validators import (
    validar_stock_minimo,
    validar_fecha_vencimiento,
    validar_codigo_medicamento,
)
from farmasur.validators.recetas.validators import (
    validar_cantidad_dosis,
    validar_fecha_receta,
    validar_dias_vigencia,
)
from farmasur.validators.ventas.validators import (
    validar_cantidad_producto,
    validar_precio,
    validar_pago,
)

__all__ = [
    # Usuarios
    'validar_rut',
    'validar_email',
    'validar_contrasena',
    # Inventario
    'validar_stock_minimo',
    'validar_fecha_vencimiento',
    'validar_codigo_medicamento',
    # Recetas
    'validar_cantidad_dosis',
    'validar_fecha_receta',
    'validar_dias_vigencia',
    # Ventas
    'validar_cantidad_producto',
    'validar_precio',
    'validar_pago',
]
