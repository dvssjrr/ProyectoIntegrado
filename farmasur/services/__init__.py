"""
Capa de Servicios
Lógica de negocio centralizada y operaciones transaccionales
"""

from farmasur.services.usuarios.services import (
    UsuarioService,
    LogAuditoriaService,
)
from farmasur.services.inventario.services import (
    LoteService,
    StockService,
    MermaService,
)
from farmasur.services.recetas.services import (
    RecetaService,
    RecetaRetenidaISPService,
    UnidosisAsistencialService,
)
from farmasur.services.ventas.services import (
    CajaService,
    POSService,
    ConvenioService,
    ComprobanteService,
)

__all__ = [
    # Usuarios
    'UsuarioService',
    'LogAuditoriaService',
    # Inventario
    'LoteService',
    'StockService',
    'MermaService',
    # Recetas
    'RecetaService',
    'RecetaRetenidaISPService',
    'UnidosisAsistencialService',
    # Ventas
    'CajaService',
    'POSService',
    'ConvenioService',
    'ComprobanteService',
]
