"""
Capa de Vistas REST
ViewSets de Django REST Framework para todos los endpoints
"""

from farmasur.views.usuarios.views import (
    UsuarioViewSet,
    AuditoriaViewSet,
)
from farmasur.views.inventario.views import (
    LaboratorioViewSet,
    ProductoViewSet,
    LoteViewSet,
    MermaViewSet,
)
from farmasur.views.recetas.views import (
    RecetaViewSet,
    RecetaRetenidaISPViewSet,
    UnidosisAsistencialViewSet,
)
from farmasur.views.ventas.views import (
    CajaDiariaViewSet,
    POSViewSet,
    ConvenioIsapreViewSet,
)

__all__ = [
    # Usuarios
    'UsuarioViewSet',
    'AuditoriaViewSet',
    # Inventario
    'LaboratorioViewSet',
    'ProductoViewSet',
    'LoteViewSet',
    'MermaViewSet',
    # Recetas
    'RecetaViewSet',
    'RecetaRetenidaISPViewSet',
    'UnidosisAsistencialViewSet',
    # Ventas
    'CajaDiariaViewSet',
    'POSViewSet',
    'ConvenioIsapreViewSet',
]
