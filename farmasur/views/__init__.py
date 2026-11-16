"""
Capa de Vistas REST
ViewSets de Django REST Framework para todos los endpoints
"""

from farmasur.views.usuarios.views import (
    UsuarioViewSet,
    LogAuditoriaViewSet,
)
from farmasur.views.inventario.views import (
    LaboratorioViewSet,
    ProductoViewSet,
    LoteViewSet,
    MermaViewSet,
)
from farmasur.views.recetas.views import (
    RecetaViewSet,
    DetalleRecetaViewSet,
    LibroISPViewSet,
)
from farmasur.views.ventas.views import (
    VentaViewSet,
    DetalleVentaViewSet,
    CajaViewSet,
)

__all__ = [
    # Usuarios
    'UsuarioViewSet',
    'LogAuditoriaViewSet',
    # Inventario
    'LaboratorioViewSet',
    'ProductoViewSet',
    'LoteViewSet',
    'MermaViewSet',
    # Recetas
    'RecetaViewSet',
    'DetalleRecetaViewSet',
    'LibroISPViewSet',
    # Ventas
    'VentaViewSet',
    'DetalleVentaViewSet',
    'CajaViewSet',
]
