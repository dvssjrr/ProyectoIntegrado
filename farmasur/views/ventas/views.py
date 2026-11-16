"""
Vistas (ViewSets) para la app ventas.
Endpoints API REST con DRF.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from farmasur.views.filters import DjangoFilterBackend
from rest_framework import filters as drf_filters

from farmasur.models import CajaDiaria, POS, ConvenioIsapre, Comprobante
from farmasur.serializers.ventas.serializers import (
    CajaDiariaListSerializer,
    CajaDiariaDetailSerializer,
    POSListSerializer,
    POSDetailSerializer,
    ConvenioIsapreSerializer,
    ComprobanteListSerializer,
    ComprobanteDetailSerializer,
)
from farmasur.services.ventas.services import CajaService, POSService, ConvenioService, ComprobanteService
from farmasur.permissions.ventas.permissions import PuedeVerVentas, PuedeModificarVentas, PuedeGestionarCaja


class CajaDiariaViewSet(viewsets.ModelViewSet):
    """CRUD para cajas diarias."""
    queryset = CajaDiaria.objects.all()
    serializer_class = CajaDiariaDetailSerializer
    permission_classes = [IsAuthenticated, PuedeGestionarCaja]
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_fields = ['caja_id', 'turno', 'estado', 'fecha']
    ordering_fields = ['fecha', 'hora_apertura']
    ordering = ['-fecha']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CajaDiariaListSerializer
        return CajaDiariaDetailSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, PuedeGestionarCaja])
    def cerrar(self, request, pk=None):
        """Cierra una caja."""
        monto_cierre = request.data.get('monto_cierre')
        notas = request.data.get('notas', '')
        
        if not monto_cierre:
            return Response(
                {'error': 'Se requiere monto_cierre'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            caja = CajaService.cerrar_caja(pk, int(monto_cierre), notas)
            serializer = self.get_serializer(caja)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (ValueError, CajaDiaria.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, PuedeGestionarCaja])
    def abierta_hoy(self, request):
        """Retorna cajas abiertas del dÃ­a."""
        cajas = CajaDiaria.objects.filter(
            estado=CajaDiaria.Estado.ABIERTA
        )
        serializer = self.get_serializer(cajas, many=True)
        return Response(serializer.data)


class POSViewSet(viewsets.ModelViewSet):
    """CRUD para ventas POS."""
    queryset = POS.objects.all()
    serializer_class = POSDetailSerializer
    permission_classes = [IsAuthenticated, PuedeModificarVentas]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['caja', 'tipo_comprobante', 'rut_cliente']
    search_fields = ['folio', 'nombre_cliente']
    ordering_fields = ['fecha_venta', 'total']
    ordering = ['-fecha_venta']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return POSListSerializer
        return POSDetailSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, PuedeVerVentas])
    def por_caja(self, request):
        """Retorna ventas de una caja especÃ­fica."""
        caja_id = request.query_params.get('caja_id')
        
        if not caja_id:
            return Response(
                {'error': 'Se requiere caja_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ventas = POSService.listar_ventas_por_caja(caja_id)
        serializer = self.get_serializer(ventas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, PuedeVerVentas])
    def total_diario(self, request):
        """Retorna total de ventas del dÃ­a."""
        from datetime import date
        
        hoy = date.today()
        ventas_hoy = POS.objects.filter(
            fecha_venta__date=hoy
        )
        
        total = sum(v.total for v in ventas_hoy)
        cantidad = ventas_hoy.count()
        
        return Response({
            'fecha': hoy,
            'cantidad_ventas': cantidad,
            'total': total,
            'promedio': int(total / cantidad) if cantidad > 0 else 0
        })


class ConvenioIsapreViewSet(viewsets.ModelViewSet):
    """CRUD para convenios Isapre."""
    queryset = ConvenioIsapre.objects.all()
    serializer_class = ConvenioIsapreSerializer
    permission_classes = [IsAuthenticated, PuedeGestionarCaja]
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ['nombre']
    ordering_fields = ['nombre', 'porcentaje_descuento']
    ordering = ['nombre']
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, PuedeVerVentas])
    def activos(self, request):
        """Retorna solo convenios activos."""
        convenios = ConvenioIsapre.objects.filter(activo=True)
        serializer = self.get_serializer(convenios, many=True)
        return Response(serializer.data)


class ComprobanteViewSet(viewsets.ReadOnlyModelViewSet):
    """Vista de solo lectura para comprobantes."""
    queryset = Comprobante.objects.all()
    serializer_class = ComprobanteDetailSerializer
    permission_classes = [IsAuthenticated, PuedeVerVentas]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['tipo', 'estado']
    search_fields = ['folio_comprobante', 'nombre_receptor']
    ordering_fields = ['fecha_emision', 'total']
    ordering = ['-fecha_emision']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ComprobanteListSerializer
        return ComprobanteDetailSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, PuedeGestionarCaja])
    def anular(self, request, pk=None):
        """Anula un comprobante."""
        notas = request.data.get('notas', '')
        
        try:
            comprobante = ComprobanteService.anular_comprobante(pk, notas)
            serializer = self.get_serializer(comprobante)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (ValueError, Comprobante.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
