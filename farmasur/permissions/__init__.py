"""
Capa de Permisos
Control de acceso basado en roles (RBAC) para todos los endpoints
"""

from farmasur.permissions.usuarios.permissions import (
    EsAdmin,
    EsAdminOLectura,
    EsUsuarioMismoOAdmin,
    es_admin,
)
from farmasur.permissions.inventario.permissions import (
    PuedeVerInventario,
    PuedeModificarInventario,
    SoloBodeguero,
)
from farmasur.permissions.recetas.permissions import (
    PuedeVerRecetas,
    SoloFarmaceutico,
    PuedeModificarRecetas,
)
from farmasur.permissions.ventas.permissions import (
    PuedeVerVentas,
    PuedeModificarVentas,
    PuedeGestionarCaja,
)

__all__ = [
    # Usuarios
    'EsAdmin',
    'EsAdminOLectura',
    'EsUsuarioMismoOAdmin',
    'es_admin',
    # Inventario
    'PuedeVerInventario',
    'PuedeModificarInventario',
    'SoloBodeguero',
    # Recetas
    'PuedeVerRecetas',
    'SoloFarmaceutico',
    'PuedeModificarRecetas',
    # Ventas
    'PuedeVerVentas',
    'PuedeModificarVentas',
    'PuedeGestionarCaja',
]
