"""
URLs para la app inventario.
Enrutamiento de endpoints de API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from farmasur.views.inventario import views

app_name = 'inventario'

router = DefaultRouter()
router.register(r'laboratorios', views.LaboratorioViewSet, basename='laboratorio')
router.register(r'productos', views.ProductoViewSet, basename='producto')
router.register(r'lotes', views.LoteViewSet, basename='lote')
router.register(r'mermas', views.MermaViewSet, basename='merma')

urlpatterns = [
    path('', include(router.urls)),
]
