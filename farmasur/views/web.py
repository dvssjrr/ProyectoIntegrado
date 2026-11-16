"""Interfaz web (HTML) de la farmacia. Los templates viven en farmasur_templates."""
import uuid
from datetime import timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q, Sum
from django.db.models.functions import Coalesce, TruncDate
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from farmasur.forms.web import (
    AbrirCajaForm, CerrarCajaForm, ConvenioForm, LaboratorioForm, LoteForm,
    MermaWebForm, ProductoForm, RechazoForm, RecetaWebForm, TransferirForm,
    UsuarioWebForm, VentaForm,
)
from farmasur.models.inventario.models import Laboratorio, Lote, Merma, Producto
from farmasur.models.recetas.models import Receta, RecetaRetenidaISP, UnidosisAsistencial
from farmasur.models.usuarios.models import Usuario
from farmasur.models.ventas.models import CajaDiaria, ConvenioIsapre, POS
from farmasur.services.inventario.services import MermaService, StockService
from farmasur.services.recetas.services import RecetaService
from farmasur.services.ventas.services import CajaService, POSService

R = Usuario.Rol
INVENTARIO = (R.FARMACEUTICO, R.BODEGUERO)
VENTAS = (R.FARMACEUTICO, R.TECNICO)
ERRORES = (ValueError, ValidationError, Receta.DoesNotExist, CajaDiaria.DoesNotExist)
PARTICIPIO = {'aprobar': 'aprobada', 'rechazar': 'rechazada', 'dispensar': 'dispensada'}


def rol_requerido(*roles):
    """Permite el acceso a los roles indicados y siempre al administrador."""
    def decorador(vista):
        @wraps(vista)
        @login_required
        def envoltura(request, *args, **kwargs):
            if request.user.rol != R.ADMIN and request.user.rol not in roles:
                return HttpResponseForbidden('No tienes permiso para ver esta página.')
            return vista(request, *args, **kwargs)
        return envoltura
    return decorador


def _mensaje_error(request, exc):
    messages.error(request, ' '.join(getattr(exc, 'messages', None) or [str(exc)]))


def _formulario(request, form, titulo, destino, subtitulo='', boton='Guardar'):
    return render(request, 'base/form.html', {
        'form': form, 'titulo': titulo, 'subtitulo': subtitulo, 'destino': destino, 'boton': boton})


# ---------------------------------------------------------------- Inicio
def _estado_lote(lote, hoy):
    dias = (lote.fecha_vencimiento - hoy).days
    if dias <= 30:
        return ('Vencido' if dias < 0 else f'Vence en {dias} días'), 'danger'
    if lote.stock_vitrina < lote.producto.stock_minimo_vitrina:
        return 'Reponer vitrina', 'warning'
    return 'Stock normal', 'success'


@login_required
def inicio(request):
    hoy = timezone.localdate()
    lotes = Lote.objects.filter(activo=True).select_related('producto')
    q, estado = request.GET.get('q', '').strip(), request.GET.get('estado', '')

    criticos = Producto.objects.filter(activo=True).annotate(
        vit=Coalesce(Sum('lotes__stock_vitrina', filter=Q(lotes__activo=True)), 0)
    ).filter(vit__lt=F('stock_minimo_vitrina')).count()
    por_vencer = lotes.filter(fecha_vencimiento__lte=hoy + timedelta(days=30)).count()

    tabla = lotes
    if q:
        tabla = tabla.filter(Q(producto__nombre_comercial__icontains=q) | Q(codigo_lote__icontains=q)
                             | Q(producto__sku_codigo_barra__icontains=q))
    venc = Q(fecha_vencimiento__lte=hoy + timedelta(days=30))
    bajo = Q(stock_vitrina__lt=F('producto__stock_minimo_vitrina'))
    if estado == 'venc':
        tabla = tabla.filter(venc)
    elif estado == 'reponer':
        tabla = tabla.filter(bajo).exclude(venc)
    elif estado == 'normal':
        tabla = tabla.exclude(venc).exclude(bajo)
    pagina = Paginator(tabla.order_by('fecha_vencimiento', 'producto__nombre_comercial'), 8).get_page(
        request.GET.get('page'))
    for lote in pagina:
        lote.estado_txt, lote.estado_color = _estado_lote(lote, hoy)

    ventas = {r['d']: r['t'] for r in POS.objects.filter(
        fecha_venta__date__gte=hoy - timedelta(days=6)).annotate(d=TruncDate('fecha_venta'))
        .values('d').annotate(t=Sum('total'))}
    dias = [hoy - timedelta(days=i) for i in range(6, -1, -1)]
    maximo = max([ventas.get(d, 0) for d in dias] + [1])
    grafico = [{'dia': d.strftime('%d/%m'), 'monto': ventas.get(d, 0),
                'alto': max(int(ventas.get(d, 0) * 100 / maximo), 2)} for d in dias]

    def contar(a, b):
        return lotes.filter(fecha_vencimiento__gte=hoy + timedelta(days=a),
                            fecha_vencimiento__lte=hoy + timedelta(days=b)).count()
    periodos = [('0-15 días', contar(0, 15), 'danger'), ('16-30 días', contar(16, 30), 'warning'),
                ('31-90 días', contar(31, 90), 'success')]
    total_periodos = sum(p[1] for p in periodos) or 1

    return render(request, 'inicio.html', {
        'criticos': criticos, 'por_vencer': por_vencer,
        'retenidas_hoy': RecetaRetenidaISP.objects.filter(fecha_dispensacion__date=hoy).count(),
        'pagina': pagina, 'q': q, 'estado': estado, 'total_lotes': tabla.count(),
        'grafico': grafico, 'total_semana': sum(ventas.values()),
        'periodos': [(n, c, col, int(c * 100 / total_periodos)) for n, c, col in periodos],
        'hoy': hoy,
    })


# ------------------------------------------------------------- Inventario
@login_required
def productos(request):
    q = request.GET.get('q', '').strip()
    lista = Producto.objects.select_related('laboratorio').order_by('nombre_comercial')
    if q:
        lista = lista.filter(Q(nombre_comercial__icontains=q) | Q(sku_codigo_barra__icontains=q)
                             | Q(principio_activo__icontains=q))
    pagina = Paginator(lista, 12).get_page(request.GET.get('page'))
    return render(request, 'inventario/productos.html', {'pagina': pagina, 'q': q})


@rol_requerido(*INVENTARIO)
def producto_form(request, pk=None):
    instancia = get_object_or_404(Producto, pk=pk) if pk else None
    form = ProductoForm(request.POST or None, instance=instancia)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Producto guardado.')
        return redirect('productos')
    return _formulario(request, form, 'Editar producto' if pk else 'Nuevo producto', 'productos')


@login_required
def inventario(request):
    hoy = timezone.localdate()
    q = request.GET.get('q', '').strip()
    lista = Lote.objects.filter(activo=True).select_related('producto')
    if q:
        lista = lista.filter(Q(producto__nombre_comercial__icontains=q) | Q(codigo_lote__icontains=q))
    pagina = Paginator(lista.order_by('fecha_vencimiento'), 12).get_page(request.GET.get('page'))
    for lote in pagina:
        lote.estado_txt, lote.estado_color = _estado_lote(lote, hoy)
    return render(request, 'inventario/lotes.html', {'pagina': pagina, 'q': q})


@rol_requerido(*INVENTARIO)
def lote_nuevo(request):
    form = LoteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Lote ingresado al inventario.')
        return redirect('inventario')
    return _formulario(request, form, 'Ingresar lote', 'inventario',
                       'Registro de recepción de mercadería.')


@rol_requerido(*INVENTARIO)
def transferir(request):
    form = TransferirForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        try:
            with transaction.atomic():
                StockService.transferir_stock(d['producto'].pk, d['cantidad'], d['origen'], d['destino'])
            messages.success(request, 'Movimiento registrado.')
            return redirect('inventario')
        except ERRORES as exc:
            _mensaje_error(request, exc)
    return _formulario(request, form, 'Registrar movimiento', 'inventario',
                       'Mueve stock entre bodega y vitrina (FEFO).', 'Registrar movimiento')


@rol_requerido(*INVENTARIO)
def mermas(request):
    lista = Merma.objects.select_related('lote__producto').order_by('-fecha_registro')
    pagina = Paginator(lista, 12).get_page(request.GET.get('page'))
    return render(request, 'inventario/mermas.html', {
        'pagina': pagina, 'total_unidades': lista.aggregate(t=Sum('cantidad'))['t'] or 0})


@rol_requerido(*INVENTARIO)
def merma_nueva(request):
    form = MermaWebForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        try:
            with transaction.atomic():
                merma = Merma.objects.create(lote=d['lote'], cantidad=d['cantidad'],
                                             razon=d['razon'], descripcion=d['descripcion'])
                MermaService.registrar_merma(merma)
            messages.success(request, 'Merma registrada y stock descontado.')
            return redirect('mermas')
        except ERRORES as exc:
            _mensaje_error(request, exc)
    return _formulario(request, form, 'Registrar merma', 'mermas')


# --------------------------------------------------------------- Recetas
@rol_requerido(*VENTAS)
def libro(request):
    estado = request.GET.get('estado', '')
    lista = Receta.objects.order_by('-fecha_registro')
    if estado:
        lista = lista.filter(estado=estado)
    return render(request, 'recetas/libro.html', {
        'pagina': Paginator(lista, 12).get_page(request.GET.get('page')),
        'estado': estado, 'estados': Receta.Estado.choices,
        'retenidas': RecetaRetenidaISP.objects.select_related('receta').order_by('-fecha_dispensacion')[:10],
        'unidosis': UnidosisAsistencial.objects.order_by('-fecha_solicitud')[:10],
        'puede_validar': request.user.rol in (R.ADMIN, R.FARMACEUTICO),
    })


@rol_requerido(*VENTAS)
def receta_nueva(request):
    form = RecetaWebForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        try:
            RecetaService.crear_receta(
                folio=f'R-{uuid.uuid4().hex[:8].upper()}', rut_paciente=d['rut_paciente'],
                nombre_paciente=d['nombre_paciente'], rut_medico=d['rut_medico'],
                nombre_medico=d['nombre_medico'], fecha_emision=d['fecha_emision'],
                medicamentos=[{'sku': d['producto'].sku_codigo_barra, 'cantidad': d['cantidad'],
                               'instrucciones': d['instrucciones']}])
            messages.success(request, 'Receta registrada.')
            return redirect('libro')
        except ERRORES as exc:
            _mensaje_error(request, exc)
    return _formulario(request, form, 'Registrar receta', 'libro')


@require_POST
@rol_requerido(R.FARMACEUTICO)
def receta_accion(request, pk, accion):
    if accion not in PARTICIPIO:
        return HttpResponseForbidden('Acción desconocida.')
    try:
        if accion == 'aprobar':
            RecetaService.aprobar_receta(pk, request.user)
        elif accion == 'rechazar':
            RecetaService.rechazar_receta(pk, request.POST.get('razon') or 'Rechazada por el químico farmacéutico')
        else:
            RecetaService.dispensar_receta(pk)
        messages.success(request, f'Receta {PARTICIPIO[accion]}.')
    except ERRORES as exc:
        _mensaje_error(request, exc)
    return redirect('libro')


# ---------------------------------------------------------------- Ventas
@rol_requerido(*VENTAS)
def caja(request):
    abrir = AbrirCajaForm(prefix='abrir')
    cerrar = CerrarCajaForm(prefix='cerrar')
    if request.method == 'POST':
        if 'abrir' in request.POST:
            abrir = AbrirCajaForm(request.POST, prefix='abrir')
            if abrir.is_valid():
                d = abrir.cleaned_data
                try:
                    CajaService.abrir_caja(d['caja_id'], d['turno'], request.user, d['monto_inicial'])
                    messages.success(request, 'Caja abierta.')
                    return redirect('caja')
                except ERRORES as exc:
                    _mensaje_error(request, exc)
        elif 'cerrar' in request.POST:
            cerrar = CerrarCajaForm(request.POST, prefix='cerrar')
            if cerrar.is_valid():
                try:
                    c = CajaService.cerrar_caja(request.POST.get('caja_pk'),
                                                cerrar.cleaned_data['monto_cierre'],
                                                cerrar.cleaned_data['notas'])
                    messages.success(request, f'Caja cerrada. Diferencia: ${c.diferencia}.')
                    return redirect('caja')
                except ERRORES as exc:
                    _mensaje_error(request, exc)
    return render(request, 'ventas/caja.html', {
        'abiertas': CajaDiaria.objects.filter(estado=CajaDiaria.Estado.ABIERTA).select_related('operario'),
        'recientes': CajaDiaria.objects.exclude(estado=CajaDiaria.Estado.ABIERTA).order_by('-hora_apertura')[:8],
        'abrir': abrir, 'cerrar': cerrar,
    })


@rol_requerido(*VENTAS)
def pos(request):
    caja_abierta = CajaDiaria.objects.filter(estado=CajaDiaria.Estado.ABIERTA).order_by('-hora_apertura').first()
    form = VentaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid() and caja_abierta:
        d = form.cleaned_data
        try:
            with transaction.atomic():
                venta = POSService.crear_venta(
                    caja=caja_abierta, folio=f'V-{uuid.uuid4().hex[:8].upper()}',
                    operario=request.user, items=d['items'], tipo_comprobante=d['tipo_comprobante'],
                    rut_cliente=d['rut_cliente'], nombre_cliente=d['nombre_cliente'],
                    convenio_id=d['convenio'].pk if d['convenio'] else None)
            messages.success(request, f'Venta {venta.folio} registrada por ${venta.total}.')
            return redirect('pos')
        except ERRORES as exc:
            _mensaje_error(request, exc)
    hoy = timezone.localdate()
    ventas = POS.objects.filter(fecha_venta__date=hoy).order_by('-fecha_venta')
    return render(request, 'ventas/pos.html', {
        'form': form, 'caja': caja_abierta, 'ventas': ventas[:10],
        'total_hoy': ventas.aggregate(t=Sum('total'))['t'] or 0,
    })


# --------------------------------------------------------- Configuración
@rol_requerido()
def configuracion(request):
    return render(request, 'usuarios/configuracion.html', {
        'usuarios': Usuario.objects.order_by('rol', 'nombre_completo'),
        'laboratorios': Laboratorio.objects.order_by('nombre'),
        'convenios': ConvenioIsapre.objects.order_by('nombre'),
    })


@rol_requerido()
def usuario_nuevo(request):
    form = UsuarioWebForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        Usuario.objects.create_user(
            username=d['username'], email=d['email'], password=d['password'],
            nombre_completo=d['nombre_completo'], rut=d['rut'], rol=d['rol'])
        messages.success(request, 'Usuario creado.')
        return redirect('configuracion')
    return _formulario(request, form, 'Nuevo usuario', 'configuracion')


@require_POST
@rol_requerido()
def usuario_toggle(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario == request.user:
        messages.error(request, 'No puedes desactivar tu propio usuario.')
    else:
        usuario.activo = usuario.is_active = not usuario.activo
        usuario.save()
        messages.success(request, f'Usuario {"activado" if usuario.activo else "desactivado"}.')
    return redirect('configuracion')


@rol_requerido()
def laboratorio_nuevo(request):
    form = LaboratorioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Laboratorio creado.')
        return redirect('configuracion')
    return _formulario(request, form, 'Nuevo laboratorio', 'configuracion')


@rol_requerido()
def convenio_nuevo(request):
    form = ConvenioForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Convenio creado.')
        return redirect('configuracion')
    return _formulario(request, form, 'Nuevo convenio', 'configuracion')
