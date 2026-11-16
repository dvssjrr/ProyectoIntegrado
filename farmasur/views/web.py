"""Interfaces web (HTML) por rol. Los templates viven en farmasur_templates."""
from datetime import timedelta
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.utils import timezone

from farmasur.models.inventario.models import Lote, Merma, Producto
from farmasur.models.recetas.models import Receta, UnidosisAsistencial
from farmasur.models.usuarios.models import LogAuditoria, Usuario
from farmasur.models.ventas.models import CajaDiaria, POS

PANEL_POR_ROL = {
    Usuario.Rol.ADMIN: 'panel_admin',
    Usuario.Rol.FARMACEUTICO: 'panel_farmaceutico',
    Usuario.Rol.TECNICO: 'panel_tecnico',
    Usuario.Rol.BODEGUERO: 'panel_bodeguero',
}


def rol_requerido(rol):
    """Permite el acceso al rol indicado y al administrador."""
    def decorador(vista):
        @wraps(vista)
        @login_required
        def envoltura(request, *args, **kwargs):
            if request.user.rol not in (rol, Usuario.Rol.ADMIN):
                return HttpResponseForbidden('No tienes permiso para ver esta interfaz.')
            return vista(request, *args, **kwargs)
        return envoltura
    return decorador


@login_required
def inicio(request):
    return redirect(PANEL_POR_ROL.get(request.user.rol, 'login'))


@rol_requerido(Usuario.Rol.ADMIN)
def panel_admin(request):
    return render(request, 'usuarios/panel_admin.html', {
        'usuarios': Usuario.objects.order_by('rol', 'nombre_completo'),
        'auditoria': LogAuditoria.objects.select_related('usuario').order_by('-timestamp')[:15],
        'total_productos': Producto.objects.filter(activo=True).count(),
        'total_ventas': POS.objects.count(),
        'monto_ventas': POS.objects.aggregate(t=Sum('total'))['t'] or 0,
    })


@rol_requerido(Usuario.Rol.FARMACEUTICO)
def panel_farmaceutico(request):
    return render(request, 'recetas/panel_farmaceutico.html', {
        'recetas_pendientes': Receta.objects.filter(estado=Receta.Estado.PENDIENTE).order_by('fecha_emision'),
        'recetas_recientes': Receta.objects.exclude(estado=Receta.Estado.PENDIENTE).order_by('-fecha_registro')[:10],
        'unidosis': UnidosisAsistencial.objects.filter(
            estado=UnidosisAsistencial.Estado.SOLICITADA).order_by('fecha_solicitud'),
    })


@rol_requerido(Usuario.Rol.TECNICO)
def panel_tecnico(request):
    hoy = timezone.localdate()
    return render(request, 'ventas/panel_tecnico.html', {
        'cajas': CajaDiaria.objects.filter(estado=CajaDiaria.Estado.ABIERTA).select_related('operario'),
        'ventas': POS.objects.filter(fecha_venta__date=hoy).order_by('-fecha_venta')[:15],
        'total_hoy': POS.objects.filter(fecha_venta__date=hoy).aggregate(t=Sum('total'))['t'] or 0,
        'productos': Producto.objects.filter(activo=True).select_related('laboratorio').order_by('nombre_comercial')[:20],
    })


@rol_requerido(Usuario.Rol.BODEGUERO)
def panel_bodeguero(request):
    limite = timezone.localdate() + timedelta(days=90)
    lotes = Lote.objects.filter(activo=True).select_related('producto')
    return render(request, 'inventario/panel_bodeguero.html', {
        'lotes': lotes.order_by('fecha_vencimiento')[:25],
        'por_vencer': lotes.filter(fecha_vencimiento__lte=limite).order_by('fecha_vencimiento')[:10],
        'stock_bajo': lotes.filter(stock_vitrina__lt=F('producto__stock_minimo_vitrina'))[:10],
        'mermas': Merma.objects.select_related('lote__producto').order_by('-fecha_registro')[:10],
    })
