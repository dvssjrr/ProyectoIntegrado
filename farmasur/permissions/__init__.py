"""
Capa de Permisos
Control de acceso basado en roles (RBAC) para todos los endpoints
"""

from farmasur.permissions.usuarios.permissions import (
    IsAdmin,
    IsFarmaceutico,
    IsOwner,
    CustomPermission,
)
from farmasur.permissions.inventario.permissions import (
    CanViewInventario,
    CanEditInventario,
    CanManageStock,
)
from farmasur.permissions.recetas.permissions import (
    CanViewRecetas,
    CanRegisterReceta,
)
from farmasur.permissions.ventas.permissions import (
    CanViewVentas,
    CanRegisterVenta,
)

__all__ = [
    # Usuarios
    'IsAdmin',
    'IsFarmaceutico',
    'IsOwner',
    'CustomPermission',
    # Inventario
    'CanViewInventario',
    'CanEditInventario',
    'CanManageStock',
    # Recetas
    'CanViewRecetas',
    'CanRegisterReceta',
    # Ventas
    'CanViewVentas',
    'CanRegisterVenta',
]
