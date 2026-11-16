"""
Capa de URLs
Enrutamiento centralizado para todos los endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importar ViewSets de cada app
from farmasur.views.usuarios.views import UsuarioViewSet, AuditoriaViewSet
from farmasur.views.inventario.views import (
    LaboratorioViewSet,
    ProductoViewSet,
    LoteViewSet,
    MermaViewSet,
)
from farmasur.views.recetas.views import RecetaViewSet, RecetaRetenidaISPViewSet, UnidosisAsistencialViewSet
from farmasur.views.ventas.views import CajaDiariaViewSet, POSViewSet, ConvenioIsapreViewSet

# Crear router
router = DefaultRouter()

# Registrar ViewSets de Usuarios
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'auditoria', AuditoriaViewSet, basename='auditoria')

# Registrar ViewSets de Inventario
router.register(r'laboratorios', LaboratorioViewSet, basename='laboratorio')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'lotes', LoteViewSet, basename='lote')
router.register(r'mermas', MermaViewSet, basename='merma')

# Registrar ViewSets de Recetas
router.register(r'recetas', RecetaViewSet, basename='receta')
router.register(r'recetas-retenidas', RecetaRetenidaISPViewSet, basename='receta-retenida')
router.register(r'unidosis', UnidosisAsistencialViewSet, basename='unidosis')

# Registrar ViewSets de Ventas
router.register(r'cajas', CajaDiariaViewSet, basename='caja')
router.register(r'ventas', POSViewSet, basename='venta')
router.register(r'convenios', ConvenioIsapreViewSet, basename='convenio')

urlpatterns = [
    path('', include(router.urls)),
]
