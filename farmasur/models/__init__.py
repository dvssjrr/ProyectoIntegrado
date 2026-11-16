"""
Capa de Modelos de Datos
Centraliza todas las entidades y relaciones de la base de datos
"""

from farmasur.models.usuarios.models import Usuario, LogAuditoria
from farmasur.models.inventario.models import (
    Laboratorio,
    Producto,
    Lote,
    RecepcionProveedor,
    Merma,
)
from farmasur.models.recetas.models import Receta, DetalleReceta, RecetaRetenidaISP, UnidosisAsistencial
from farmasur.models.ventas.models import CajaDiaria, POS, ConvenioIsapre, Comprobante

__all__ = [
    # Usuarios
    'Usuario',
    'LogAuditoria',
    # Inventario
    'Laboratorio',
    'Producto',
    'Lote',
    'RecepcionProveedor',
    'Merma',
    # Recetas
    'Receta',
    'DetalleReceta',
    'RecetaRetenidaISP',
    'UnidosisAsistencial',
    # Ventas
    'CajaDiaria',
    'POS',
    'ConvenioIsapre',
    'Comprobante',
]
