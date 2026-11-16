"""
Capa de Serializadores
Validación y transformación de datos para la API REST
"""

from farmasur.serializers.usuarios.serializers import (
    UsuarioListSerializer,
    UsuarioDetailSerializer,
    LogAuditoriaSerializer,
)
from farmasur.serializers.inventario.serializers import (
    LaboratorioSerializer,
    ProductoListSerializer,
    ProductoDetailSerializer,
    LoteListSerializer,
    LoteDetailSerializer,
    RecepcionProveedorSerializer,
    MermaSerializer,
)
from farmasur.serializers.recetas.serializers import (
    RecetaListSerializer,
    RecetaDetailSerializer,
    RecetaRetenidaISPSerializer,
    UnidosisAsistencialListSerializer,
    UnidosisAsistencialDetailSerializer,
)
from farmasur.serializers.ventas.serializers import (
    CajaDiariaListSerializer,
    CajaDiariaDetailSerializer,
    POSListSerializer,
    POSDetailSerializer,
    ConvenioIsapreSerializer,
    ComprobanteListSerializer,
    ComprobanteDetailSerializer,
)

__all__ = [
    # Usuarios
    'UsuarioListSerializer',
    'UsuarioDetailSerializer',
    'LogAuditoriaSerializer',
    # Inventario
    'LaboratorioSerializer',
    'ProductoListSerializer',
    'ProductoDetailSerializer',
    'LoteListSerializer',
    'LoteDetailSerializer',
    'RecepcionProveedorSerializer',
    'MermaSerializer',
    # Recetas
    'RecetaListSerializer',
    'RecetaDetailSerializer',
    'RecetaRetenidaISPSerializer',
    'UnidosisAsistencialListSerializer',
    'UnidosisAsistencialDetailSerializer',
    # Ventas
    'CajaDiariaListSerializer',
    'CajaDiariaDetailSerializer',
    'POSListSerializer',
    'POSDetailSerializer',
    'ConvenioIsapreSerializer',
    'ComprobanteListSerializer',
    'ComprobanteDetailSerializer',
]
