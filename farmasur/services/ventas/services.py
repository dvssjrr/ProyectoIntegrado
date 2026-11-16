"""
Servicios para la app ventas.
Lógica de negocio reutilizable y operaciones transaccionales.
"""
from django.db import transaction
from django.utils import timezone
from farmasur.models import CajaDiaria, POS, ConvenioIsapre, Comprobante
from farmasur.models import Lote, Producto
from farmasur.services.inventario.services import LoteService, StockService
from datetime import datetime, timedelta


class CajaService:
    """Servicio para gestión de caja diaria."""
    
    @staticmethod
    @transaction.atomic
    def abrir_caja(caja_id, turno, operario, monto_inicial):
        """Abre una nueva caja diaria."""
        # Verificar si ya existe una caja abierta para ese turno
        caja_existente = CajaDiaria.objects.filter(
            caja_id=caja_id,
            fecha=timezone.now().date(),
            turno=turno,
            estado=CajaDiaria.Estado.ABIERTA
        ).first()
        
        if caja_existente:
            raise ValueError(f"Ya existe una caja abierta para {turno}")
        
        caja = CajaDiaria.objects.create(
            caja_id=caja_id,
            turno=turno,
            operario=operario,
            monto_inicial=monto_inicial
        )
        return caja
    
    @staticmethod
    @transaction.atomic
    def cerrar_caja(caja_id, monto_cierre, notas=''):
        """Cierra una caja y calcula diferencia."""
        caja = CajaDiaria.objects.get(id=caja_id)
        
        if caja.estado != CajaDiaria.Estado.ABIERTA:
            raise ValueError(f"La caja debe estar abierta. Estado: {caja.estado}")
        
        caja.monto_cierre = monto_cierre
        caja.diferencia = monto_cierre - caja.monto_inicial - caja.total_ventas
        caja.estado = CajaDiaria.Estado.CERRADA
        caja.hora_cierre = timezone.now()
        caja.notas = notas
        caja.datos_cierre = {
            'monto_inicial': caja.monto_inicial,
            'monto_cierre': monto_cierre,
            'total_ventas': caja.total_ventas,
            'total_descuentos': caja.total_descuentos,
            'diferencia': caja.diferencia,
            'fecha_cierre': caja.hora_cierre.isoformat()
        }
        caja.save()
        return caja
    
    @staticmethod
    def obtener_caja_abierta(caja_id, turno=None):
        """Obtiene caja abierta del día."""
        query = CajaDiaria.objects.filter(
            caja_id=caja_id,
            fecha=timezone.now().date(),
            estado=CajaDiaria.Estado.ABIERTA
        )
        
        if turno:
            query = query.filter(turno=turno)
        
        return query.first()


class POSService:
    """Servicio para gestión de ventas POS."""
    
    @staticmethod
    @transaction.atomic
    def crear_venta(caja, folio, operario, items, tipo_comprobante='BOLETA',
                    rut_cliente='', nombre_cliente='', convenio_id=None,
                    requiere_receta=False, requiere_unidosis=False):
        """Crea una nueva venta POS con actualización de lotes."""
        
        # Validar que caja esté abierta
        if caja.estado != CajaDiaria.Estado.ABIERTA:
            raise ValueError("La caja debe estar abierta")
        
        # Calcular totales
        subtotal = 0
        descuento_convenio = 0
        
        for item in items:
            subtotal += item.get('precio_unitario', 0) * item.get('cantidad', 0)
        
        # Aplicar convenio si existe
        porcentaje_descuento = 0
        if convenio_id:
            convenio = ConvenioIsapre.objects.get(id=convenio_id)
            if convenio.activo:
                porcentaje_descuento = convenio.porcentaje_descuento
                descuento_potencial = int(subtotal * (porcentaje_descuento / 100))
                
                if convenio.monto_maximo_descuento:
                    descuento_convenio = min(descuento_potencial, convenio.monto_maximo_descuento)
                else:
                    descuento_convenio = descuento_potencial
        
        total = subtotal - descuento_convenio
        
        # Crear venta
        venta = POS.objects.create(
            caja=caja,
            folio=folio,
            operario=operario,
            rut_cliente=rut_cliente,
            nombre_cliente=nombre_cliente,
            tipo_comprobante=tipo_comprobante,
            subtotal=subtotal,
            descuento_total=descuento_convenio,
            total=total,
            convenio_aplicado=ConvenioIsapre.objects.get(id=convenio_id).nombre if convenio_id else '',
            porcentaje_descuento_convenio=porcentaje_descuento,
            requiere_receta_retenida=requiere_receta,
            requiere_unidosis=requiere_unidosis,
            items=items
        )
        
        # Actualizar totales de caja
        caja.total_ventas += total
        caja.total_descuentos += descuento_convenio
        caja.save()
        
        # Dispensar lotes usando FEFO para cada medicamento (sku = código de barras del producto)
        for item in items:
            if 'sku' in item and 'cantidad' in item:
                producto = Producto.objects.get(sku_codigo_barra=item['sku'])
                LoteService.dispensar_lote_fefo(
                    producto_id=producto.pk,
                    cantidad=item['cantidad'],
                    usuario=operario
                )
        
        return venta
    
    @staticmethod
    def obtener_venta(venta_id):
        """Obtiene una venta por ID."""
        return POS.objects.get(id=venta_id)
    
    @staticmethod
    def listar_ventas_por_caja(caja_id):
        """Retorna todas las ventas de una caja."""
        return POS.objects.filter(caja_id=caja_id).order_by('-fecha_venta')


class ConvenioService:
    """Servicio para gestión de convenios Isapre."""
    
    @staticmethod
    @transaction.atomic
    def crear_convenio(nombre, porcentaje_descuento, descripcion='',
                      medicamentos_excluidos=None, monto_maximo=None,
                      requiere_qf=False):
        """Crea un nuevo convenio Isapre."""
        
        if porcentaje_descuento < 0 or porcentaje_descuento > 100:
            raise ValueError("Porcentaje debe estar entre 0 y 100")
        
        convenio = ConvenioIsapre.objects.create(
            nombre=nombre,
            porcentaje_descuento=porcentaje_descuento,
            descripcion=descripcion,
            medicamentos_excluidos=medicamentos_excluidos or [],
            monto_maximo_descuento=monto_maximo,
            requiere_autorizacion_qf=requiere_qf
        )
        return convenio
    
    @staticmethod
    @transaction.atomic
    def actualizar_convenio(convenio_id, **kwargs):
        """Actualiza un convenio existente."""
        convenio = ConvenioIsapre.objects.get(id=convenio_id)
        
        for key, value in kwargs.items():
            if hasattr(convenio, key):
                setattr(convenio, key, value)
        
        convenio.save()
        return convenio


class ComprobanteService:
    """Servicio para gestión de comprobantes."""
    
    @staticmethod
    @transaction.atomic
    def crear_comprobante(venta_pos, tipo, folio_comprobante, nombre_receptor,
                         rut_receptor='', giro_receptor='', direccion_receptor=''):
        """Crea un comprobante para una venta."""
        
        # Calcular IVA (19% en Chile)
        tasa_iva = 0.19
        neto = int(venta_pos.total / (1 + tasa_iva))
        iva = venta_pos.total - neto
        
        comprobante = Comprobante.objects.create(
            venta_pos=venta_pos,
            tipo=tipo,
            folio_comprobante=folio_comprobante,
            rut_receptor=rut_receptor,
            nombre_receptor=nombre_receptor,
            giro_receptor=giro_receptor,
            direccion_receptor=direccion_receptor,
            neto=neto,
            iva=iva,
            total=venta_pos.total
        )
        
        return comprobante
    
    @staticmethod
    @transaction.atomic
    def anular_comprobante(comprobante_id, notas=''):
        """Anula un comprobante."""
        comprobante = Comprobante.objects.get(id=comprobante_id)
        
        if comprobante.estado == 'ANULADA':
            raise ValueError("El comprobante ya está anulado")
        
        comprobante.estado = 'ANULADA'
        comprobante.notas = notas
        comprobante.save()
        
        return comprobante
