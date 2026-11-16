"""
URLs para la app usuarios.
Enrutamiento de endpoints de API y vistas.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from farmasur.views.usuarios import views

app_name = 'usuarios'

router = DefaultRouter()
router.register(r'usuarios', views.UsuarioViewSet, basename='usuario')
router.register(r'auditoria', views.AuditoriaViewSet, basename='auditoria')

urlpatterns = [
    path('', include(router.urls)),
]
