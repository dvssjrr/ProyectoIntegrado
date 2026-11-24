"""Interfaz web (HTML) de la farmacia. Los templates viven en farmasur_templates."""
import uuid
from datetime import timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce, TruncDate
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST
import json
from urllib.parse import urlencode

from farmasur.forms.web import (
    AbrirCajaForm, CerrarCajaForm, ClienteWebForm, ConvenioForm, LaboratorioForm, LoteForm,
    MermaWebForm, ProductoForm, RechazoForm, RecetaWebForm, TransferirForm,
    UsuarioWebForm, VentaForm,
)
from farmasur.models.inventario.models import Laboratorio, Lote, Merma, Producto
from farmasur.models.recetas.models import Receta, RecetaRetenidaISP, UnidosisAsistencial
from farmasur.models.usuarios.models import LogAuditoria, Usuario
from farmasur.models.ventas.models import CajaDiaria, Cliente, ConvenioIsapre, POS, Comprobante
from farmasur.services.inventario.services import MermaService, StockService
from farmasur.services.recetas.services import RecetaService
from farmasur.services.ventas.services import CajaService, POSService
from farmasur.services.ventas.reportes import exportar_excel_ventas, exportar_pdf_ventas

R = Usuario.Rol
INVENTARIO = (R.FARMACEUTICO, R.BODEGUERO)
VENTAS = (R.FARMACEUTICO, R.TECNICO)
LIBRO = (R.FARMACEUTICO, R.TECNICO)
ERRORES = (ValueError, ValidationError, Receta.DoesNotExist, CajaDiaria.DoesNotExist)
PARTICIPIO = {'aprobar': 'aprobada', 'rechazar': 'rechazada', 'dispensar': 'dispensada'}


def rol_requerido(*roles):
    """Permite el acceso solo a los roles indicados. Admin se incluye solo si está en la lista."""
    def decorador(vista):
        @wraps(vista)
        @login_required
        def envoltura(request, *args, **kwargs):
            if roles and request.user.rol not in roles:
                return HttpResponseForbidden('No tienes permiso para ver esta página.')
            if not roles and request.user.rol != R.ADMIN:
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
    categoria = request.GET.get('categoria', '')
    lista = Producto.objects.select_related('laboratorio').order_by('nombre_comercial')
    if q:
        lista = lista.filter(Q(nombre_comercial__icontains=q) | Q(sku_codigo_barra__icontains=q)
                             | Q(principio_activo__icontains=q))
    if categoria in Producto.Categoria.values:
        lista = lista.filter(categoria=categoria)
    pagina = Paginator(lista, 12).get_page(request.GET.get('page'))
    return render(request, 'inventario/productos.html', {
        'pagina': pagina, 'q': q, 'categoria': categoria, 'categorias': Producto.Categoria.choices,
    })


@rol_requerido(R.ADMIN)
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


@rol_requerido(R.ADMIN, R.BODEGUERO)
def lote_nuevo(request):
    form = LoteForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Lote ingresado al inventario.')
        return redirect('inventario')
    return _formulario(request, form, 'Ingresar lote', 'inventario',
                       'Registro de recepción de mercadería.')


@rol_requerido(R.ADMIN, R.BODEGUERO)
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


@rol_requerido(R.ADMIN, R.FARMACEUTICO)
def mermas(request):
    lista = Merma.objects.select_related('lote__producto').order_by('-fecha_registro')
    pagina = Paginator(lista, 12).get_page(request.GET.get('page'))
    return render(request, 'inventario/mermas.html', {
        'pagina': pagina, 'total_unidades': lista.aggregate(t=Sum('cantidad'))['t'] or 0})


@rol_requerido(R.ADMIN, R.FARMACEUTICO)
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
@rol_requerido(R.ADMIN, R.FARMACEUTICO, R.TECNICO)
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
        'puede_validar': request.user.rol == R.FARMACEUTICO,
    })


@rol_requerido(R.FARMACEUTICO, R.TECNICO)
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
@rol_requerido(R.FARMACEUTICO, R.TECNICO)
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
    abiertas = list(CajaDiaria.objects.filter(
        estado=CajaDiaria.Estado.ABIERTA
    ).select_related('operario'))
    recientes = list(CajaDiaria.objects.exclude(
        estado=CajaDiaria.Estado.ABIERTA
    ).order_by('-hora_apertura')[:8])
    etiquetas_pago = dict(POS.MetodoPago.choices)
    for caja_resumen in abiertas + recientes:
        caja_resumen.resumen_pagos = [
            {
                'metodo': etiquetas_pago[item['metodo_pago']],
                'total': item['total'],
                'cantidad': item['cantidad'],
            }
            for item in POS.objects.filter(caja=caja_resumen).values('metodo_pago').annotate(
                total=Sum('total'), cantidad=Count('id')
            )
        ]
    return render(request, 'ventas/caja.html', {
        'abiertas': abiertas,
        'recientes': recientes,
        'abrir': abrir, 'cerrar': cerrar,
    })


@login_required
def buscar_producto_codigo(request):
    """Busca producto por código de barras / SKU para el POS."""
    codigo = request.GET.get('codigo', '').strip()
    if not codigo:
        return JsonResponse({'ok': False, 'error': 'Código no proporcionado.'}, status=400)
    
    prod = Producto.objects.filter(activo=True, sku_codigo_barra=codigo).first()

    if not prod:
        return JsonResponse({'ok': False, 'error': f'No se encontró producto con código "{codigo}".'}, status=404)

    return JsonResponse({
        'ok': True,
        'sku': prod.sku_codigo_barra,
        'nombre': prod.nombre_comercial,
        'principio': prod.principio_activo,
        'presentacion': prod.presentacion,
        'precio': prod.precio_clp,
        'stock_vitrina': prod.stock_total_vitrina,
        'stock_bodega': prod.stock_total_bodega,
        'condicion_venta': prod.condicion_venta,
        'condicion_display': prod.get_condicion_venta_display(),
        'categoria': prod.categoria,
        'categoria_display': prod.get_categoria_display(),
        'frio': prod.requiere_cadena_frio,
    })


@rol_requerido(R.FARMACEUTICO, R.TECNICO)
def pos(request):
    caja_abierta = CajaDiaria.objects.filter(estado=CajaDiaria.Estado.ABIERTA).order_by('-hora_apertura').first()
    form = VentaForm(request.POST or None)

    if request.method == 'POST' and caja_abierta:
        # Modo escaneo con lector / cámara (items_json)
        items_json_raw = request.POST.get('items_json')
        if items_json_raw:
            try:
                items_data = json.loads(items_json_raw)
                if not items_data:
                    messages.error(request, 'Debe escanear o agregar al menos un producto a la venta.')
                    return redirect('pos')

                items = []
                for it in items_data:
                    sku = str(it.get('sku', '')).strip()
                    cant = int(it.get('cantidad', 1))
                    if sku and cant > 0:
                        prod = Producto.objects.get(sku_codigo_barra=sku, activo=True)
                        items.append({
                            'sku': prod.sku_codigo_barra,
                            'nombre': prod.nombre_comercial,
                            'presentacion': prod.presentacion,
                            'cantidad': cant,
                            'precio_unitario': prod.precio_clp,
                            'subtotal': cant * prod.precio_clp
                        })

                if not items:
                    messages.error(request, 'No se identificaron productos válidos para cobrar.')
                    return redirect('pos')

                convenio_id = request.POST.get('convenio')
                tipo_comprobante = request.POST.get('tipo_comprobante', 'BOLETA')
                rut_cliente = request.POST.get('rut_cliente', '').strip()
                nombre_cliente = request.POST.get('nombre_cliente', '').strip()

                with transaction.atomic():
                    venta = POSService.crear_venta(
                        caja=caja_abierta, folio=f'V-{uuid.uuid4().hex[:8].upper()}',
                        operario=request.user, items=items, tipo_comprobante=tipo_comprobante,
                        rut_cliente=rut_cliente, nombre_cliente=nombre_cliente,
                        convenio_id=int(convenio_id) if convenio_id else None,
                        metodo_pago=request.POST.get('medio_pago', 'EFECTIVO'),
                        banco_tarjeta=request.POST.get('banco_tarjeta', ''),
                        receta_folio=request.POST.get('receta_folio', ''),
                        autorizado_por_qf=request.user if request.user.rol == R.FARMACEUTICO else None,
                        confirmacion_qf=request.POST.get('confirmacion_qf') == 'on',
                    )
                messages.success(request, f'¡Venta {venta.folio} registrada exitosamente! Boleta emitida.')
                return redirect('boleta', venta_id=venta.id)
            except Exception as exc:
                _mensaje_error(request, exc)
                return redirect('pos')
        elif form.is_valid():
            d = form.cleaned_data
            try:
                with transaction.atomic():
                    venta = POSService.crear_venta(
                        caja=caja_abierta, folio=f'V-{uuid.uuid4().hex[:8].upper()}',
                        operario=request.user, items=d['items'], tipo_comprobante=d['tipo_comprobante'],
                        rut_cliente=d['rut_cliente'], nombre_cliente=d['nombre_cliente'],
                        convenio_id=d['convenio'].pk if d['convenio'] else None,
                        metodo_pago=request.POST.get('medio_pago', 'EFECTIVO'),
                        banco_tarjeta=request.POST.get('banco_tarjeta', ''),
                        receta_folio=request.POST.get('receta_folio', ''),
                        autorizado_por_qf=request.user if request.user.rol == R.FARMACEUTICO else None,
                        confirmacion_qf=request.POST.get('confirmacion_qf') == 'on')
                messages.success(request, f'Venta {venta.folio} registrada por ${venta.total}. Boleta emitida.')
                return redirect('boleta', venta_id=venta.id)
            except ERRORES as exc:
                _mensaje_error(request, exc)

    hoy = timezone.localdate()
    ventas = POS.objects.filter(fecha_venta__date=hoy).select_related('comprobante').order_by('-fecha_venta')
    convenios = ConvenioIsapre.objects.filter(activo=True).order_by('nombre')
    productos_rapidos = Producto.objects.filter(activo=True).order_by('nombre_comercial')[:10]

    return render(request, 'ventas/pos.html', {
        'form': form,
        'caja': caja_abierta,
        'ventas': ventas[:12],
        'total_hoy': ventas.aggregate(t=Sum('total'))['t'] or 0,
        'convenios': convenios,
        'productos_rapidos': productos_rapidos,
        'es_qf': request.user.rol == R.FARMACEUTICO,
    })


@rol_requerido(R.FARMACEUTICO, R.TECNICO)
def buscar_cliente_rut(request):
    rut = request.GET.get('rut', '').strip().replace('.', '').replace('-', '').upper()
    if not rut:
        return JsonResponse({'ok': False, 'error': 'Ingresa un RUT.'}, status=400)
    cliente = Cliente.objects.select_related('convenio').filter(rut=rut).first()
    if not cliente:
        return JsonResponse({'ok': False, 'error': 'No hay una ficha de cliente registrada con ese RUT.'}, status=404)
    compras = POS.objects.filter(Q(cliente=cliente) | Q(rut_cliente=cliente.rut))
    return JsonResponse({
        'ok': True,
        'rut': cliente.rut,
        'nombre': cliente.nombre_completo,
        'email': cliente.email,
        'telefono': cliente.telefono,
        'convenio_id': cliente.convenio_id,
        'convenio': cliente.convenio.nombre if cliente.convenio else '',
        'compras': compras.count(),
    })


@login_required
def ver_boleta(request, venta_id):
    """Muestra e imprime la boleta electrónica asociada a una venta,
    incluyendo el código de barras y boleta individual por cada producto."""
    from farmasur.services.barcode import generar_codigo_barra_svg

    venta = get_object_or_404(POS.objects.select_related('caja', 'operario'), id=venta_id)
    comprobante = getattr(venta, 'comprobante', None)
    if not comprobante:
        tasa_iva = 0.19
        neto = int(venta.total / (1 + tasa_iva))
        iva = venta.total - neto
        tipo_comp = 'FACTURA' if venta.tipo_comprobante == 'FACTURA' else 'BOLETA'
        comprobante = Comprobante.objects.create(
            venta_pos=venta,
            tipo=tipo_comp,
            folio_comprobante=f"BOL-{venta.id:06d}",
            rut_receptor=venta.rut_cliente or '66.666.666-6',
            nombre_receptor=venta.nombre_cliente or 'Cliente General',
            neto=neto,
            iva=iva,
            total=venta.total
        )

    # Código de barras oficial del comprobante general
    codigo_boleta_svg = generar_codigo_barra_svg(comprobante.folio_comprobante, height=42, show_text=True)

    # Generar código de barra y boleta individual para CADA producto comprado
    items_enriquecidos = []
    dscto_pct = venta.porcentaje_descuento_convenio or 0

    for idx, item in enumerate(venta.items or [], 1):
        sku = str(item.get('sku', '')).strip()
        nombre = item.get('nombre', 'Producto')
        presentacion = item.get('presentacion', '')
        cant = int(item.get('cantidad', 1))
        precio_unit = int(item.get('precio_unitario', 0))
        subtotal_item = cant * precio_unit

        # Descuento proporcional
        total_item = int(subtotal_item * (1 - dscto_pct / 100))
        neto_item = int(total_item / 1.19)
        iva_item = total_item - neto_item
        folio_item = f"{comprobante.folio_comprobante}-P{idx:02d}"

        # Código de barras del producto (SKU) y del ticket individual
        codigo_prod = sku if sku else f"MED{idx:04d}"
        barcode_item_svg = generar_codigo_barra_svg(codigo_prod, height=44, show_text=True)
        barcode_ticket_svg = generar_codigo_barra_svg(folio_item, height=40, show_text=True)

        items_enriquecidos.append({
            'numero': idx,
            'sku': sku,
            'nombre': nombre,
            'presentacion': presentacion,
            'cantidad': cant,
            'precio_unitario': precio_unit,
            'subtotal': subtotal_item,
            'total_item': total_item,
            'neto_item': neto_item,
            'iva_item': iva_item,
            'folio_item': folio_item,
            'barcode_svg': barcode_item_svg,
            'barcode_ticket_svg': barcode_ticket_svg,
            'lotes_dispensados': item.get('lotes_dispensados', []),
            'stock_restante': item.get('stock_restante', 0),
        })

    return render(request, 'ventas/boleta.html', {
        'venta': venta,
        'comprobante': comprobante,
        'codigo_boleta_svg': codigo_boleta_svg,
        'items_enriquecidos': items_enriquecidos,
        'boletas_individuales': items_enriquecidos,
        'total_productos': len(items_enriquecidos),
    })


# --------------------------------------------------------- Configuración
@rol_requerido()
def configuracion(request):
    return render(request, 'usuarios/configuracion.html', {
        'usuarios': Usuario.objects.order_by('rol', 'nombre_completo'),
        'laboratorios': Laboratorio.objects.order_by('nombre'),
        'convenios': ConvenioIsapre.objects.order_by('nombre'),
        'clientes': Cliente.objects.select_related('convenio').order_by('nombre_completo'),
    })


@rol_requerido()
def usuario_nuevo(request):
    form = UsuarioWebForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        usuario = Usuario.objects.create_user(
            username=d['username'], email=d['email'], password=d['password'],
            nombre_completo=d['nombre_completo'], rut=d['rut'], rol=d['rol'])
        LogAuditoria.registrar(
            request.user, LogAuditoria.TipoEvento.CAMBIO_USUARIO,
            f'Creó usuario {usuario.username}.',
            {'usuario_id': usuario.pk, 'rut': usuario.rut},
            request.META.get('REMOTE_ADDR'), request.META.get('HTTP_USER_AGENT', ''))
        messages.success(request, 'Usuario creado.')
        return redirect('configuracion')
    return _formulario(request, form, 'Nuevo usuario', 'configuracion')


@rol_requerido()
def usuario_editar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario.rol == R.ADMIN:
        return HttpResponseForbidden('Las cuentas de administrador no se pueden editar desde otra cuenta.')
    form = UsuarioWebForm(request.POST or None, instance=usuario, initial={
        'username': usuario.username, 'nombre_completo': usuario.nombre_completo,
        'rut': usuario.rut, 'email': usuario.email, 'rol': usuario.rol,
    })
    if request.method == 'POST' and form.is_valid():
        datos = form.cleaned_data
        usuario.username = datos['username']
        usuario.nombre_completo = datos['nombre_completo']
        usuario.rut = datos['rut']
        usuario.email = datos['email']
        usuario.rol = datos['rol']
        if datos['password']:
            usuario.set_password(datos['password'])
        usuario.save()
        LogAuditoria.registrar(
            request.user, LogAuditoria.TipoEvento.CAMBIO_USUARIO,
            f'Editó usuario {usuario.username}.',
            {'usuario_id': usuario.pk, 'rut': usuario.rut},
            request.META.get('REMOTE_ADDR'), request.META.get('HTTP_USER_AGENT', ''))
        messages.success(request, 'Usuario actualizado.')
        return redirect('configuracion')
    return _formulario(request, form, 'Editar usuario', 'configuracion')


@require_POST
@rol_requerido()
def usuario_toggle(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if usuario.rol == R.ADMIN:
        messages.error(request, 'Las cuentas de administrador no se pueden activar o desactivar desde otra cuenta.')
    elif usuario == request.user:
        messages.error(request, 'No puedes desactivar tu propio usuario.')
    else:
        usuario.activo = usuario.is_active = not usuario.activo
        usuario.save()
        LogAuditoria.registrar(
            request.user, LogAuditoria.TipoEvento.CAMBIO_USUARIO,
            f'{"Activó" if usuario.activo else "Desactivó"} usuario {usuario.username}.',
            {'usuario_id': usuario.pk, 'rut': usuario.rut, 'activo': usuario.activo},
            request.META.get('REMOTE_ADDR'), request.META.get('HTTP_USER_AGENT', ''))
        messages.success(request, f'Usuario {"activado" if usuario.activo else "desactivado"}.')
    return redirect('configuracion')


@rol_requerido()
def clientes(request):
    query = request.GET.get('q', '').strip()
    lista = Cliente.objects.select_related('convenio').order_by('nombre_completo')
    if query:
        lista = lista.filter(
            Q(nombre_completo__icontains=query) | Q(rut__icontains=query) | Q(email__icontains=query)
        )
    pagina = Paginator(lista, 20).get_page(request.GET.get('page'))
    for cliente in pagina:
        cliente.compras_total = POS.objects.filter(
            Q(cliente=cliente) | Q(rut_cliente=cliente.rut)
        ).count()
    return render(request, 'usuarios/clientes.html', {
        'pagina': pagina,
        'q': query,
    })


@rol_requerido()
def cliente_nuevo(request):
    form = ClienteWebForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        Cliente.objects.create(**form.cleaned_data)
        messages.success(request, 'Cliente registrado. Su ficha y beneficios estarán disponibles en el POS.')
        return redirect('clientes')
    return _formulario(request, form, 'Registrar cliente', 'clientes')


@rol_requerido()
def historial_compras_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    compras = POS.objects.filter(
        Q(cliente=cliente) | Q(rut_cliente=cliente.rut)
    ).select_related('operario').order_by('-fecha_venta')
    return render(request, 'usuarios/historial_compras.html', {
        'cliente': cliente,
        'compras': Paginator(compras, 30).get_page(request.GET.get('page')),
        'total_compras': compras.count(),
        'monto_total': compras.aggregate(total=Sum('total'))['total'] or 0,
    })


@rol_requerido()
def auditoria(request):
    registros = LogAuditoria.objects.select_related('usuario').order_by('-timestamp')
    tipo = request.GET.get('tipo', '').strip()
    usuario = request.GET.get('usuario', '').strip()
    desde_raw, hasta_raw = request.GET.get('desde', ''), request.GET.get('hasta', '')
    desde, hasta = parse_date(desde_raw), parse_date(hasta_raw)
    if (desde_raw and not desde) or (hasta_raw and not hasta):
        return HttpResponseBadRequest('Formato de fecha inválido.')
    if tipo:
        registros = registros.filter(tipo_evento=tipo)
    if usuario:
        registros = registros.filter(
            Q(usuario__nombre_completo__icontains=usuario) | Q(usuario__rut__icontains=usuario)
            | Q(usuario__username__icontains=usuario)
        )
    if desde:
        registros = registros.filter(timestamp__date__gte=desde)
    if hasta:
        registros = registros.filter(timestamp__date__lte=hasta)
    return render(request, 'usuarios/auditoria.html', {
        'pagina': Paginator(registros, 30).get_page(request.GET.get('page')),
        'tipos': LogAuditoria.TipoEvento.choices, 'tipo': tipo, 'usuario': usuario,
        'desde': desde_raw, 'hasta': hasta_raw,
    })


def _consulta_reporte_ventas(parametros):
    desde_raw = parametros.get('desde', '')
    hasta_raw = parametros.get('hasta', '')
    desde, hasta = parse_date(desde_raw), parse_date(hasta_raw)
    if (desde_raw and not desde) or (hasta_raw and not hasta):
        return None, None
    if not desde and not hasta:
        desde = timezone.localdate() - timedelta(days=29)
        desde_raw = desde.isoformat()

    ventas = POS.objects.select_related(
        'operario', 'caja', 'cliente', 'autorizado_por_qf', 'receta'
    ).order_by('-fecha_venta')
    if desde:
        ventas = ventas.filter(fecha_venta__date__gte=desde)
    if hasta:
        ventas = ventas.filter(fecha_venta__date__lte=hasta)
    metodo = parametros.get('metodo_pago', '')
    if metodo in POS.MetodoPago.values:
        ventas = ventas.filter(metodo_pago=metodo)
    busqueda = parametros.get('q', '').strip()
    if busqueda:
        ventas = ventas.filter(
            Q(folio__icontains=busqueda) | Q(rut_cliente__icontains=busqueda)
            | Q(nombre_cliente__icontains=busqueda) | Q(operario__nombre_completo__icontains=busqueda)
        )
    return ventas, {
        'desde': desde_raw,
        'hasta': hasta_raw,
        'metodo_pago': metodo,
        'q': busqueda,
        'categoria': parametros.get('categoria', ''),
    }


def _detalle_reporte_ventas(ventas):
    ventas_base = list(ventas)
    detalle = []
    totales_categoria = {}
    ventas_por_categoria = {}
    skus_sin_categoria = {
        str(item.get('sku', ''))
        for venta in ventas_base for item in (venta.items or [])
        if not item.get('categoria') and item.get('sku')
    }
    categoria_por_sku = {
        producto.sku_codigo_barra: producto.get_categoria_display()
        for producto in Producto.objects.filter(sku_codigo_barra__in=skus_sin_categoria)
    }
    for venta in ventas_base:
        for item in venta.items or []:
            nombre_categoria = item.get('categoria') or categoria_por_sku.get(
                item.get('sku'), 'Sin categoría'
            )
            totales_categoria[nombre_categoria] = totales_categoria.get(nombre_categoria, 0) + int(
                item.get('cantidad', 0)
            )
            ventas_por_categoria.setdefault(nombre_categoria, set()).add(venta.pk)
            item_datos = dict(item)
            item_datos['categoria'] = nombre_categoria
            detalle.append({
                'venta': venta,
                'item': item_datos,
                'categoria': nombre_categoria,
                'total_linea': int(item.get('cantidad', 0)) * int(item.get('precio_unitario', 0)),
            })
    return ventas_base, detalle, totales_categoria, ventas_por_categoria


@rol_requerido()
def reportes_ventas(request):
    ventas, filtros = _consulta_reporte_ventas(request.GET)
    if ventas is None:
        return HttpResponseBadRequest('Formato de fecha inválido.')
    ventas_base, detalle_completo, totales_categoria, ventas_por_categoria = _detalle_reporte_ventas(ventas)
    categoria = filtros['categoria']
    detalle = [
        linea for linea in detalle_completo
        if not categoria or linea['categoria'] == categoria
    ]
    if categoria:
        ventas = ventas.filter(pk__in=ventas_por_categoria.get(categoria, set()))
    ventas_pagina = Paginator(ventas, 30).get_page(request.GET.get('page'))
    detalle_pagina = Paginator(detalle, 50).get_page(request.GET.get('linea_page'))
    resumen = ventas.aggregate(total=Sum('total'), unidades=Sum('descuento_total'))
    return render(request, 'ventas/reportes.html', {
        'ventas': ventas_pagina,
        'detalle': detalle_pagina,
        'categorias': sorted(totales_categoria),
        'categoria': categoria,
        'categorias': sorted(totales_categoria),
        **filtros,
        'metodos_pago': POS.MetodoPago.choices,
        'cantidad_ventas': ventas.count(),
        'total_ventas': resumen['total'] or 0,
        'total_descuentos': resumen['unidades'] or 0,
        'total_items': (
            totales_categoria.get(categoria, 0) if categoria else sum(totales_categoria.values())
        ),
        'totales_categoria': totales_categoria,
    })


@require_POST
@rol_requerido()
def reportes_ventas_exportar(request):
    modo = request.POST.get('modo', '')
    formato = request.POST.get('formato', '')
    if modo not in ('seleccionadas', 'completo') or formato not in ('pdf', 'excel'):
        return HttpResponseBadRequest('Selecciona el alcance y formato de exportación.')

    ventas_consulta, filtros = _consulta_reporte_ventas(request.POST)
    if ventas_consulta is None:
        return HttpResponseBadRequest('Formato de fecha inválido.')
    filtros['alcance'] = (
        'Ventas seleccionadas' if modo == 'seleccionadas' else 'Reporte completo filtrado'
    )
    _, _, _, ventas_por_categoria = _detalle_reporte_ventas(ventas_consulta)
    categoria = filtros['categoria']
    if categoria:
        ventas_consulta = ventas_consulta.filter(
            pk__in=ventas_por_categoria.get(categoria, set())
        )

    if modo == 'seleccionadas':
        ids_recibidos = request.POST.getlist('venta_ids')
        if not ids_recibidos:
            messages.error(request, 'Marca al menos una venta o elige exportar el reporte completo.')
            filtros_url = urlencode({k: v for k, v in filtros.items() if v})
            return redirect(f"{reverse('reportes_ventas')}?{filtros_url}")
        try:
            ids = [int(value) for value in ids_recibidos]
        except ValueError:
            return HttpResponseBadRequest('La selección de ventas no es válida.')
        if len(set(ids)) != len(ids):
            return HttpResponseBadRequest('La selección contiene ventas duplicadas.')
        ventas_consulta = ventas_consulta.filter(pk__in=ids)
        if ventas_consulta.count() != len(ids):
            return HttpResponseBadRequest('La selección incluye ventas fuera de los filtros aplicados.')

    ventas = list(ventas_consulta)
    ventas, detalle, _, _ = _detalle_reporte_ventas(ventas)
    if categoria:
        detalle = [linea for linea in detalle if linea['categoria'] == categoria]

    if formato == 'excel':
        contenido = exportar_excel_ventas(ventas, detalle, filtros)
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        extension = 'xlsx'
    else:
        contenido = exportar_pdf_ventas(ventas, detalle, filtros)
        content_type = 'application/pdf'
        extension = 'pdf'
    fecha_inicio = filtros['desde'] or 'completo'
    fecha_termino = filtros['hasta'] or 'completo'
    nombre = f'reporte_ventas_{fecha_inicio}_{fecha_termino}.{extension}'
    respuesta = HttpResponse(contenido, content_type=content_type)
    disposicion = 'inline' if request.POST.get('disposicion') == 'imprimir' and formato == 'pdf' else 'attachment'
    respuesta['Content-Disposition'] = f'{disposicion}; filename="{nombre}"'
    return respuesta


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
