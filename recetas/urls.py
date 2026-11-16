"""
URLs para la app recetas.
Enrutamiento de endpoints de API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'recetas'

router = DefaultRouter()
router.register(r'recetas', views.RecetaViewSet, basename='receta')
router.register(r'recetas-retenidas', views.RecetaRetenidaISPViewSet, basename='receta-retenida')
router.register(r'unidosis', views.UnidosisAsistencialViewSet, basename='unidosis')

urlpatterns = [
    path('', include(router.urls)),
]
