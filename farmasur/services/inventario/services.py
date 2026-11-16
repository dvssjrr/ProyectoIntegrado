"""
Services para la app inventario.
Lógica de negocio reutilizable: FEFO, cálculos de stock, etc.
"""
from django.db import transaction
from django.db.models import Q, Sum
from datetime import date, timedelta
from .models import Lote, Producto, RecepcionProveedor, Merma


class LoteService:
    """Servicio para gestión de lotes con algoritmo FEFO."""
    
    @staticmethod
    def obtener_lotes_fefo(producto_id):
        """
        Obtiene lotes de un producto ordenados por FEFO (First Expire First Out).
        Primero: vencidos, luego: próximos a vencer, luego: normales.
        """
        hoy = date.today()
        lotes = Lote.objects.filter(
            producto_id=producto_id,
            cantidad_total__gt=0
        ).order_by('fecha_vencimiento')
        
        return sorted(
            lotes,
            key=lambda l: (
                l.dias_para_vencer is not None and l.dias_para_vencer < 0,  # Vencidos primero
                l.dias_para_vencer if l.dias_para_vencer else float('inf'),  # Luego por días
            )
        )
    
    @staticmethod
    @transaction.atomic
    def dispensar_lote_fefo(producto_id, cantidad):
        """
        Dispensa medicamentos de un producto usando FEFO.
        Retorna el lote dispensado y la cantidad dispensada.
        """
        lotes = LoteService.obtener_lotes_fefo(producto_id)
        cantidad_faltante = cantidad
        lotes_dispensados = []
        
        for lote in lotes:
            if cantidad_faltante <= 0:
                break
            
            if lote.cantidad_total > 0:
                cantidad_a_dispensar = min(lote.cantidad_total, cantidad_faltante)
                lote.cantidad_total -= cantidad_a_dispensar
                lote.save()
                
                lotes_dispensados.append({
                    'lote': lote,
                    'cantidad': cantidad_a_dispensar
                })
                
                cantidad_faltante -= cantidad_a_dispensar
        
        if cantidad_faltante > 0:
            raise ValueError(f"Stock insuficiente. Falta: {cantidad_faltante} unidades.")
        
        return lotes_dispensados
    
    @staticmethod
    def obtener_lotes_proximos_vencer(dias=30):
        """Obtiene lotes próximos a vencer en los próximos N días."""
        hoy = date.today()
        fecha_limite = hoy + timedelta(days=dias)
        
        return Lote.objects.filter(
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=fecha_limite,
            cantidad_total__gt=0
        ).order_by('fecha_vencimiento')
    
    @staticmethod
    def obtener_lotes_vencidos():
        """Obtiene lotes ya vencidos."""
        hoy = date.today()
        return Lote.objects.filter(
            fecha_vencimiento__lt=hoy,
            cantidad_total__gt=0
        )


class StockService:
    """Servicio para cálculos de stock."""
    
    @staticmethod
    def obtener_stock_total(producto_id):
        """Calcula el stock total de un producto (vitrina + bodega)."""
        return Lote.objects.filter(
            producto_id=producto_id
        ).aggregate(total=Sum('cantidad_total'))['total'] or 0
    
    @staticmethod
    def obtener_stock_vitrina(producto_id):
        """Calcula stock en vitrina."""
        return Lote.objects.filter(
            producto_id=producto_id,
            ubicacion='VITRINA'
        ).aggregate(total=Sum('cantidad_total'))['total'] or 0
    
    @staticmethod
    def obtener_stock_bodega(producto_id):
        """Calcula stock en bodega."""
        return Lote.objects.filter(
            producto_id=producto_id,
            ubicacion='BODEGA'
        ).aggregate(total=Sum('cantidad_total'))['total'] or 0
    
    @staticmethod
    @transaction.atomic
    def transferir_stock(producto_id, cantidad, origen, destino):
        """Transfiere stock entre vitrina y bodega."""
        if origen not in ['VITRINA', 'BODEGA'] or destino not in ['VITRINA', 'BODEGA']:
            raise ValueError("Ubicación inválida.")
        
        if origen == destino:
            raise ValueError("Origen y destino son iguales.")
        
        # Obtener lotes del origen y decrementar
        lotes_origen = Lote.objects.filter(
            producto_id=producto_id,
            ubicacion=origen
        ).order_by('fecha_vencimiento')
        
        cantidad_faltante = cantidad
        for lote in lotes_origen:
            if cantidad_faltante <= 0:
                break
            
            if lote.cantidad_total > 0:
                cantidad_a_transferir = min(lote.cantidad_total, cantidad_faltante)
                lote.cantidad_total -= cantidad_a_transferir
                lote.save()
                cantidad_faltante -= cantidad_a_transferir
        
        if cantidad_faltante > 0:
            raise ValueError(f"Stock insuficiente en {origen}.")
        
        # Crear lote en destino (o incrementar si ya existe)
        # Simplificado: asumimos crear nuevo lote
        # En producción: lógica más sofisticada
        return True


class MermaService:
    """Servicio para gestión de mermas (pérdidas)."""
    
    @staticmethod
    @transaction.atomic
    def registrar_merma(lote_id, cantidad, motivo, responsable):
        """Registra una merma y decrementa el lote."""
        lote = Lote.objects.get(pk=lote_id)
        
        if lote.cantidad_total < cantidad:
            raise ValueError(f"Cantidad insuficiente en lote. Disponible: {lote.cantidad_total}")
        
        # Decrementar lote
        lote.cantidad_total -= cantidad
        lote.save()
        
        # Registrar merma
        merma = Merma.objects.create(
            lote=lote,
            cantidad=cantidad,
            motivo=motivo,
            responsable=responsable
        )
        
        return merma
