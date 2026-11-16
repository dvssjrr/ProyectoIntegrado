"""
Capa de URLs
Enrutamiento centralizado para todos los endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importar ViewSets de cada app
from farmasur.views.usuarios.views import UsuarioViewSet, LogAuditoriaViewSet
from farmasur.views.inventario.views import (
    MedicamentoViewSet,
    StockVitrinaViewSet,
    StockBodegaViewSet,
    MovimientoInventarioViewSet,
    LoteViewSet,
)
from farmasur.views.recetas.views import RecetaViewSet, DetalleRecetaViewSet, LibroISPViewSet
from farmasur.views.ventas.views import VentaViewSet, DetalleVentaViewSet, CajaViewSet

# Crear router
router = DefaultRouter()

# Registrar ViewSets de Usuarios
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'auditoria', LogAuditoriaViewSet, basename='auditoria')

# Registrar ViewSets de Inventario
router.register(r'medicamentos', MedicamentoViewSet, basename='medicamento')
router.register(r'stock-vitrina', StockVitrinaViewSet, basename='stock-vitrina')
router.register(r'stock-bodega', StockBodegaViewSet, basename='stock-bodega')
router.register(r'movimientos', MovimientoInventarioViewSet, basename='movimiento')
router.register(r'lotes', LoteViewSet, basename='lote')

# Registrar ViewSets de Recetas
router.register(r'recetas', RecetaViewSet, basename='receta')
router.register(r'detalles-receta', DetalleRecetaViewSet, basename='detalle-receta')
router.register(r'libro-isp', LibroISPViewSet, basename='libro-isp')

# Registrar ViewSets de Ventas
router.register(r'ventas', VentaViewSet, basename='venta')
router.register(r'detalles-venta', DetalleVentaViewSet, basename='detalle-venta')
router.register(r'cajas', CajaViewSet, basename='caja')

urlpatterns = [
    path('', include(router.urls)),
]
