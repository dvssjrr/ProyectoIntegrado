from django.contrib.auth import views as auth_views
from django.urls import path

from farmasur.views import web

urlpatterns = [
    path('', web.inicio, name='inicio'),
    path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('productos/', web.productos, name='productos'),
    path('productos/nuevo/', web.producto_form, name='producto_nuevo'),
    path('productos/<int:pk>/editar/', web.producto_form, name='producto_editar'),
    path('inventario/', web.inventario, name='inventario'),
    path('inventario/lote/nuevo/', web.lote_nuevo, name='lote_nuevo'),
    path('inventario/movimiento/', web.transferir, name='transferir'),
    path('mermas/', web.mermas, name='mermas'),
    path('mermas/nueva/', web.merma_nueva, name='merma_nueva'),

    path('libro/', web.libro, name='libro'),
    path('libro/receta/nueva/', web.receta_nueva, name='receta_nueva'),
    path('libro/receta/<int:pk>/<str:accion>/', web.receta_accion, name='receta_accion'),

    path('ventas/', web.pos, name='pos'),
    path('ventas/buscar-producto/', web.buscar_producto_codigo, name='buscar_producto_codigo'),
    path('ventas/boleta/<int:venta_id>/', web.ver_boleta, name='boleta'),
    path('caja/', web.caja, name='caja'),

    path('configuracion/', web.configuracion, name='configuracion'),
    path('configuracion/usuarios/nuevo/', web.usuario_nuevo, name='usuario_nuevo'),
    path('configuracion/usuarios/<int:pk>/activar/', web.usuario_toggle, name='usuario_toggle'),
    path('configuracion/laboratorios/nuevo/', web.laboratorio_nuevo, name='laboratorio_nuevo'),
    path('configuracion/convenios/nuevo/', web.convenio_nuevo, name='convenio_nuevo'),
]
