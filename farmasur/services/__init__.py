"""
Capa de Servicios
Lógica de negocio centralizada y operaciones transaccionales
"""

from farmasur.services.usuarios.services import (
    UsuarioService,
    LogAuditoriaService,
    autenticar_usuario,
)
from farmasur.services.inventario.services import (
    LoteService,
    StockService,
    MermaService,
)
from farmasur.services.recetas.services import (
    RecetaService,
    validar_receta_legal,
    registrar_en_libro_isp,
)
from farmasur.services.ventas.services import (
    VentaService,
    CajaService,
    calcular_convenio_isapre,
)

__all__ = [
    # Usuarios
    'UsuarioService',
    'LogAuditoriaService',
    'autenticar_usuario',
    # Inventario
    'LoteService',
    'StockService',
    'MermaService',
    # Recetas
    'RecetaService',
    'validar_receta_legal',
    'registrar_en_libro_isp',
    # Ventas
    'VentaService',
    'CajaService',
    'calcular_convenio_isapre',
]
