"""
Services para la app inventario.
Lógica de negocio reutilizable: FEFO, cálculos de stock, etc.
"""
from datetime import date, timedelta

from django.db import transaction
from django.db.models import F, Sum

from farmasur.models import Lote, Producto

UBICACIONES = {'VITRINA': 'stock_vitrina', 'BODEGA': 'stock_bodega'}


def _stock_lote(lote):
    return lote.stock_vitrina + lote.stock_bodega


class LoteService:
    """Servicio para gestión de lotes con algoritmo FEFO."""

    @staticmethod
    def _lotes_disponibles(producto_id):
        hoy = date.today()
        return [
            lote for lote in Lote.objects.filter(
                producto_id=producto_id,
                activo=True,
                bloqueado_vencimiento=False,
                fecha_vencimiento__gte=hoy,
            ).order_by('fecha_vencimiento')
            if _stock_lote(lote) > 0
        ]

    @staticmethod
    def obtener_lotes_fefo(producto_id):
        """Lotes vigentes con stock, el que vence primero va primero."""
        if not Producto.objects.filter(pk=producto_id).exists():
            raise Producto.DoesNotExist
        return LoteService._lotes_disponibles(producto_id)

    @staticmethod
    @transaction.atomic
    def dispensar_lote_fefo(producto_id, cantidad, usuario=None):
        """Descuenta stock (vitrina primero, luego bodega) siguiendo FEFO."""
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")
        if not Producto.objects.filter(pk=producto_id).exists():
            raise Producto.DoesNotExist

        faltante = cantidad
        dispensados = []
        for lote in Lote.objects.select_for_update().filter(
            pk__in=[l.pk for l in LoteService._lotes_disponibles(producto_id)]
        ).order_by('fecha_vencimiento'):
            if faltante <= 0:
                break
            de_vitrina = min(lote.stock_vitrina, faltante)
            de_bodega = min(lote.stock_bodega, faltante - de_vitrina)
            tomado = de_vitrina + de_bodega
            if tomado == 0:
                continue
            lote.stock_vitrina -= de_vitrina
            lote.stock_bodega -= de_bodega
            lote.save(update_fields=['stock_vitrina', 'stock_bodega', 'fecha_ultima_modificacion'])
            dispensados.append({'lote_id': lote.pk, 'codigo_lote': lote.codigo_lote, 'cantidad': tomado})
            faltante -= tomado

        if faltante > 0:
            raise ValueError(f"Stock insuficiente. Falta: {faltante} unidades.")
        return dispensados

    @staticmethod
    def obtener_lotes_proximos_vencer(dias=30):
        hoy = date.today()
        return Lote.objects.filter(
            activo=True,
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=hoy + timedelta(days=dias),
        ).order_by('fecha_vencimiento')

    @staticmethod
    def obtener_lotes_vencidos():
        return Lote.objects.filter(fecha_vencimiento__lt=date.today())


class StockService:
    """Servicio para cálculos de stock."""

    @staticmethod
    def _lotes_vigentes(producto_id):
        return Lote.objects.filter(
            producto_id=producto_id, activo=True, bloqueado_vencimiento=False
        )

    @staticmethod
    def obtener_stock_vitrina(producto_id):
        return StockService._lotes_vigentes(producto_id).aggregate(t=Sum('stock_vitrina'))['t'] or 0

    @staticmethod
    def obtener_stock_bodega(producto_id):
        return StockService._lotes_vigentes(producto_id).aggregate(t=Sum('stock_bodega'))['t'] or 0

    @staticmethod
    def calcular_stock_total(producto_id):
        if not Producto.objects.filter(pk=producto_id).exists():
            raise Producto.DoesNotExist
        return StockService.obtener_stock_vitrina(producto_id) + StockService.obtener_stock_bodega(producto_id)

    obtener_stock_total = calcular_stock_total

    @staticmethod
    def obtener_stock_todos_productos():
        filas = Lote.objects.filter(
            activo=True, bloqueado_vencimiento=False
        ).values('producto_id').annotate(
            stock_vitrina=Sum('stock_vitrina'), stock_bodega=Sum('stock_bodega')
        )
        return [
            {
                'producto_id': f['producto_id'],
                'stock_vitrina': f['stock_vitrina'] or 0,
                'stock_bodega': f['stock_bodega'] or 0,
                'stock_total': (f['stock_vitrina'] or 0) + (f['stock_bodega'] or 0),
            }
            for f in filas
        ]

    @staticmethod
    @transaction.atomic
    def transferir_stock(producto_id, cantidad, origen, destino):
        """Mueve stock entre vitrina y bodega respetando FEFO."""
        if origen not in UBICACIONES or destino not in UBICACIONES:
            raise ValueError("Ubicación inválida.")
        if origen == destino:
            raise ValueError("Origen y destino son iguales.")
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")

        campo_origen, campo_destino = UBICACIONES[origen], UBICACIONES[destino]
        faltante = cantidad
        for lote in StockService._lotes_vigentes(producto_id).select_for_update().order_by('fecha_vencimiento'):
            if faltante <= 0:
                break
            mover = min(getattr(lote, campo_origen), faltante)
            if mover <= 0:
                continue
            setattr(lote, campo_origen, F(campo_origen) - mover)
            setattr(lote, campo_destino, F(campo_destino) + mover)
            lote.save(update_fields=[campo_origen, campo_destino, 'fecha_ultima_modificacion'])
            faltante -= mover

        if faltante > 0:
            raise ValueError(f"Stock insuficiente en {origen}.")
        return True


class MermaService:
    """Servicio para gestión de mermas (pérdidas)."""

    @staticmethod
    @transaction.atomic
    def registrar_merma(merma):
        """Descuenta del lote la cantidad de una merma ya creada (vitrina primero)."""
        lote = Lote.objects.select_for_update().get(pk=merma.lote_id)
        if _stock_lote(lote) < merma.cantidad:
            raise ValueError(f"Cantidad insuficiente en lote. Disponible: {_stock_lote(lote)}")

        de_vitrina = min(lote.stock_vitrina, merma.cantidad)
        lote.stock_vitrina -= de_vitrina
        lote.stock_bodega -= merma.cantidad - de_vitrina
        lote.save(update_fields=['stock_vitrina', 'stock_bodega', 'fecha_ultima_modificacion'])
        return merma
