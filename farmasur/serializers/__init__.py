"""
Capa de Serializadores
Validación y transformación de datos para la API REST
"""

from farmasur.serializers.usuarios.serializers import (
    UsuarioSerializer,
    LogAuditoriaSerializer,
)
from farmasur.serializers.inventario.serializers import (
    LaboratorioSerializer,
    ProductoListSerializer,
    ProductoDetailSerializer,
    LoteListSerializer,
    LoteDetailSerializer,
    MermaSerializer,
)
from farmasur.serializers.recetas.serializers import (
    RecetaSerializer,
    DetalleRecetaSerializer,
    LibroISPSerializer,
)
from farmasur.serializers.ventas.serializers import (
    VentaSerializer,
    DetalleVentaSerializer,
    CajaSerializer,
)

__all__ = [
    # Usuarios
    'UsuarioSerializer',
    'LogAuditoriaSerializer',
    # Inventario
    'LaboratorioSerializer',
    'ProductoListSerializer',
    'ProductoDetailSerializer',
    'LoteListSerializer',
    'LoteDetailSerializer',
    'MermaSerializer',
    # Recetas
    'RecetaSerializer',
    'DetalleRecetaSerializer',
    'LibroISPSerializer',
    # Ventas
    'VentaSerializer',
    'DetalleVentaSerializer',
    'CajaSerializer',
]
