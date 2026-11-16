"""
URLs para la app ventas.
Enrutamiento de endpoints de API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from farmasur.views.ventas import views

app_name = 'ventas'

router = DefaultRouter()
router.register(r'cajas', views.CajaDiariaViewSet, basename='caja')
router.register(r'ventas', views.POSViewSet, basename='venta')
router.register(r'convenios', views.ConvenioIsapreViewSet, basename='convenio')
router.register(r'comprobantes', views.ComprobanteViewSet, basename='comprobante')

urlpatterns = [
    path('', include(router.urls)),
]
