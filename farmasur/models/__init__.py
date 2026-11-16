"""
Capa de Modelos de Datos
Centraliza todas las entidades y relaciones de la base de datos
"""

from farmasur.models.usuarios.models import Usuario, LogAuditoria
from farmasur.models.inventario.models import (
    Medicamento,
    StockVitrina,
    StockBodega,
    MovimientoInventario,
    Lote,
)
from farmasur.models.recetas.models import Receta, DetalleReceta, LibroISP
from farmasur.models.ventas.models import Venta, DetalleVenta, Caja

__all__ = [
    # Usuarios
    'Usuario',
    'LogAuditoria',
    # Inventario
    'Medicamento',
    'StockVitrina',
    'StockBodega',
    'MovimientoInventario',
    'Lote',
    # Recetas
    'Receta',
    'DetalleReceta',
    'LibroISP',
    # Ventas
    'Venta',
    'DetalleVenta',
    'Caja',
]
