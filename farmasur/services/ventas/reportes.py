from collections import defaultdict
from html import escape
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def _fecha(fecha):
    return fecha.strftime('%d/%m/%Y %H:%M') if fecha else ''


def _moneda(valor):
    return '$' + f'{int(valor or 0):,}'.replace(',', '.')


def _texto_excel(valor):
    texto = '' if valor is None else str(valor)
    if texto.startswith(('=', '+', '-', '@')):
        return "'" + texto
    return texto


def _resumen(ventas, detalle):
    categorias = defaultdict(int)
    pagos = defaultdict(lambda: {'cantidad': 0, 'total': 0})
    for linea in detalle:
        categorias[linea['categoria']] += int(linea['item'].get('cantidad', 0))
    for venta in ventas:
        pago = venta.get_metodo_pago_display()
        pagos[pago]['cantidad'] += 1
        pagos[pago]['total'] += venta.total
    return {
        'cantidad_ventas': len(ventas),
        'total_ventas': sum(venta.total for venta in ventas),
        'total_descuentos': sum(venta.descuento_total for venta in ventas),
        'total_unidades': sum(categorias.values()),
        'categorias': dict(sorted(categorias.items())),
        'pagos': dict(sorted(pagos.items())),
    }


def exportar_excel_ventas(ventas, detalle, filtros):
    resumen = _resumen(ventas, detalle)
    libro = Workbook()
    hoja_resumen = libro.active
    hoja_resumen.title = 'Resumen'
    encabezado = PatternFill('solid', fgColor='8E1B1B')
    fuente_encabezado = Font(color='FFFFFF', bold=True)

    hoja_resumen.append(['Reporte de ventas Farmasur'])
    hoja_resumen.append(['Periodo', filtros.get('desde') or 'Sin inicio', filtros.get('hasta') or 'Sin término'])
    hoja_resumen.append([
        'Categoría', _texto_excel(filtros.get('categoria') or 'Todas'),
        'Medio de pago', _texto_excel(filtros.get('metodo_pago') or 'Todos'),
        'Búsqueda', _texto_excel(filtros.get('q') or 'Sin búsqueda'),
        'Alcance', _texto_excel(filtros.get('alcance') or 'Reporte completo'),
    ])
    hoja_resumen.append([])
    hoja_resumen.append(['Ventas', 'Total vendido (CLP)', 'Descuentos (CLP)', 'Unidades'])
    hoja_resumen.append([
        resumen['cantidad_ventas'], resumen['total_ventas'],
        resumen['total_descuentos'], resumen['total_unidades'],
    ])
    hoja_resumen.append([])
    hoja_resumen.append(['Categoría', 'Unidades'])
    for fila in hoja_resumen.iter_rows(min_row=5, max_row=5):
        for celda in fila:
            celda.fill = encabezado
            celda.font = fuente_encabezado
    for fila in hoja_resumen.iter_rows(min_row=8, max_row=8):
        for celda in fila:
            celda.fill = encabezado
            celda.font = fuente_encabezado
    for categoria, unidades in resumen['categorias'].items():
        hoja_resumen.append([_texto_excel(categoria), unidades])
    hoja_resumen.append([])
    fila_pago_encabezado = hoja_resumen.max_row + 1
    hoja_resumen.append(['Medio de pago', 'Ventas', 'Total (CLP)'])
    for fila in hoja_resumen.iter_rows(min_row=fila_pago_encabezado, max_row=fila_pago_encabezado):
        for celda in fila:
            celda.fill = encabezado
            celda.font = fuente_encabezado
    for metodo, datos in resumen['pagos'].items():
        hoja_resumen.append([_texto_excel(metodo), datos['cantidad'], datos['total']])
    for columna, ancho in enumerate((28, 22, 24, 22, 18, 30, 18, 22), 1):
        hoja_resumen.column_dimensions[get_column_letter(columna)].width = ancho

    hoja_ventas = libro.create_sheet('Ventas')
    hoja_ventas.append([
        'Fecha y hora', 'Folio', 'Caja', 'Comprobante', 'Cliente', 'RUT cliente',
        'Operario', 'Medio de pago', 'Banco / referencia simulada', 'QF autorizador',
        'Folio receta', 'Productos', 'Subtotal CLP', 'Descuento CLP', 'Total CLP',
    ])
    for venta in ventas:
        productos = '; '.join(
            f"{item.get('nombre', 'Producto')} x{item.get('cantidad', 0)}"
            for item in (venta.items or [])
        )
        hoja_ventas.append([
            _fecha(venta.fecha_venta), _texto_excel(venta.folio),
            _texto_excel(venta.caja.caja_id), _texto_excel(venta.get_tipo_comprobante_display()),
            _texto_excel(venta.nombre_cliente or 'Cliente General'),
            _texto_excel(venta.rut_cliente), _texto_excel(venta.operario.nombre_completo),
            _texto_excel(venta.get_metodo_pago_display()),
            _texto_excel(' '.join(filter(None, [venta.banco_tarjeta, venta.referencia_pago]))),
            _texto_excel(venta.autorizado_por_qf.nombre_completo if venta.autorizado_por_qf else ''),
            _texto_excel(venta.receta.folio if venta.receta else ''),
            _texto_excel(productos), venta.subtotal, venta.descuento_total, venta.total,
        ])

    hoja_detalle = libro.create_sheet('Detalle por producto')
    hoja_detalle.append([
        'Fecha y hora', 'Folio', 'SKU', 'Producto', 'Categoría', 'Unidades',
        'Precio unitario CLP', 'Subtotal CLP', 'Medio de pago',
    ])
    for linea in detalle:
        venta, item = linea['venta'], linea['item']
        hoja_detalle.append([
            _fecha(venta.fecha_venta), _texto_excel(venta.folio),
            _texto_excel(item.get('sku', '')), _texto_excel(item.get('nombre', 'Producto')),
            _texto_excel(linea['categoria']), int(item.get('cantidad', 0)),
            int(item.get('precio_unitario', 0)), linea['total_linea'],
            _texto_excel(venta.get_metodo_pago_display()),
        ])

    for hoja in (hoja_ventas, hoja_detalle):
        hoja.freeze_panes = 'A2'
        hoja.auto_filter.ref = hoja.dimensions
        for celda in hoja[1]:
            celda.fill = encabezado
            celda.font = fuente_encabezado
            celda.alignment = Alignment(wrap_text=True, vertical='center')
        for indice, columna in enumerate(hoja.columns, 1):
            ancho = max(
                (len(str(celda.value or '')) for celda in list(columna)[:1000]),
                default=12,
            )
            hoja.column_dimensions[get_column_letter(indice)].width = min(max(ancho + 2, 12), 42)
        hoja.row_dimensions[1].height = 30

    salida = BytesIO()
    libro.save(salida)
    return salida.getvalue()


def exportar_pdf_ventas(ventas, detalle, filtros):
    resumen = _resumen(ventas, detalle)
    salida = BytesIO()
    documento = SimpleDocTemplate(
        salida, pagesize=landscape(A4), leftMargin=9 * mm, rightMargin=9 * mm,
        topMargin=12 * mm, bottomMargin=12 * mm,
    )
    estilos = getSampleStyleSheet()
    compacto = ParagraphStyle(
        'Compacto', parent=estilos['BodyText'], fontName='Helvetica', fontSize=6.5,
        leading=8, spaceAfter=0,
    )
    encabezado_celda = ParagraphStyle(
        'EncabezadoCelda', parent=compacto, fontName='Helvetica-Bold',
        textColor=colors.white,
    )

    def celda(valor, estilo=compacto):
        return Paragraph(escape(str(valor or '')), estilo)

    historia = [
        Paragraph('Reporte de ventas - Farmasur', estilos['Title']),
        Paragraph(
            f"Periodo: {escape(filtros.get('desde') or 'Sin inicio')} a "
            f"{escape(filtros.get('hasta') or 'Sin término')}",
            estilos['Normal'],
        ),
        Paragraph(
            'Filtros: '
            f"categoría {escape(filtros.get('categoria') or 'Todas')}; "
            f"pago {escape(filtros.get('metodo_pago') or 'Todos')}; "
            f"búsqueda {escape(filtros.get('q') or 'Sin búsqueda')}; "
            f"alcance {escape(filtros.get('alcance') or 'Reporte completo')}",
            estilos['Normal'],
        ),
        Spacer(1, 4 * mm),
    ]
    resumen_tabla = Table([
        ['Ventas', 'Total vendido', 'Descuentos', 'Unidades'],
        [
            str(resumen['cantidad_ventas']), _moneda(resumen['total_ventas']),
            _moneda(resumen['total_descuentos']), str(resumen['total_unidades']),
        ],
    ], colWidths=[40 * mm] * 4)
    resumen_tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e1b1b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#dddddd')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    historia.extend([resumen_tabla, Spacer(1, 5 * mm), Paragraph('Ventas', estilos['Heading2'])])

    titulos_ventas = [
        'Fecha / folio', 'Caja', 'Documento', 'Cliente / RUT', 'Operario',
        'Pago', 'Productos / autorización', 'Subtotal', 'Descuento', 'Total',
    ]
    filas_ventas = [[celda(titulo, encabezado_celda) for titulo in titulos_ventas]]
    for venta in ventas:
        productos = ', '.join(
            f"{item.get('nombre', 'Producto')} x{item.get('cantidad', 0)}"
            for item in (venta.items or [])
        )
        if venta.autorizado_por_qf:
            productos += (
                f" | QF: {venta.autorizado_por_qf.nombre_completo}"
                f" / Receta: {venta.receta.folio if venta.receta else ''}"
            )
        pago = venta.get_metodo_pago_display()
        if venta.banco_tarjeta:
            pago += f" / {venta.banco_tarjeta} {venta.referencia_pago}"
        filas_ventas.append([
            celda(f"{_fecha(venta.fecha_venta)} / {venta.folio}"),
            celda(venta.caja.caja_id), celda(venta.get_tipo_comprobante_display()),
            celda(f"{venta.nombre_cliente or 'Cliente General'} / {venta.rut_cliente}"),
            celda(venta.operario.nombre_completo),
            celda(pago), celda(productos), celda(_moneda(venta.subtotal)),
            celda(_moneda(venta.descuento_total)), celda(_moneda(venta.total)),
        ])
    tabla_ventas = Table(
        filas_ventas,
        colWidths=[25 * mm, 14 * mm, 18 * mm, 38 * mm, 26 * mm, 25 * mm, 58 * mm,
                   22 * mm, 18 * mm, 22 * mm],
        repeatRows=1,
    )
    tabla_ventas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e1b1b')),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7f3f3')]),
        ('PADDING', (0, 0), (-1, -1), 3),
    ]))
    historia.extend([tabla_ventas, Spacer(1, 5 * mm), Paragraph('Detalle por producto y categoría', estilos['Heading2'])])

    titulos_detalle = ['Fecha / folio', 'SKU', 'Producto', 'Categoría', 'Unid.', 'Precio', 'Subtotal', 'Pago']
    filas_detalle = [[celda(titulo, encabezado_celda) for titulo in titulos_detalle]]
    for linea in detalle:
        venta, item = linea['venta'], linea['item']
        filas_detalle.append([
            celda(f"{_fecha(venta.fecha_venta)} / {venta.folio}"),
            celda(item.get('sku', '')), celda(item.get('nombre', 'Producto')),
            celda(linea['categoria']), str(item.get('cantidad', 0)),
            celda(_moneda(item.get('precio_unitario', 0))),
            celda(_moneda(linea['total_linea'])),
            celda(venta.get_metodo_pago_display()),
        ])
    tabla_detalle = Table(
        filas_detalle,
        colWidths=[36 * mm, 23 * mm, 60 * mm, 34 * mm, 14 * mm, 24 * mm, 25 * mm, 25 * mm],
        repeatRows=1,
    )
    tabla_detalle.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e1b1b')),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7f3f3')]),
        ('PADDING', (0, 0), (-1, -1), 3),
    ]))
    historia.append(tabla_detalle)
    if resumen['categorias']:
        historia.extend([Spacer(1, 5 * mm), Paragraph('Unidades por categoría', estilos['Heading2'])])
        filas_categoria = [['Categoría', 'Unidades']]
        filas_categoria.extend(
            [celda(nombre), str(unidades)] for nombre, unidades in resumen['categorias'].items()
        )
        tabla_categoria = Table(filas_categoria, colWidths=[70 * mm, 30 * mm], repeatRows=1)
        tabla_categoria.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e1b1b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#cccccc')),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        historia.append(tabla_categoria)
    if resumen['pagos']:
        historia.extend([Spacer(1, 5 * mm), Paragraph('Totales por medio de pago', estilos['Heading2'])])
        filas_pago = [['Medio de pago', 'Ventas', 'Total']]
        filas_pago.extend(
            [celda(metodo), str(datos['cantidad']), celda(_moneda(datos['total']))]
            for metodo, datos in resumen['pagos'].items()
        )
        tabla_pago = Table(filas_pago, colWidths=[60 * mm, 30 * mm, 40 * mm], repeatRows=1)
        tabla_pago.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e1b1b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#cccccc')),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        historia.append(tabla_pago)

    def pie_pagina(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(landscape(A4)[0] - 9 * mm, 6 * mm, f'Página {doc.page}')
        canvas.restoreState()

    documento.build(historia, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
    return salida.getvalue()
