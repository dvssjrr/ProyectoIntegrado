"""
Vistas (ViewSets) para la app inventario.
Endpoints API REST con DRF.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from farmasur.views.filters import DjangoFilterBackend
from rest_framework import filters as drf_filters

from farmasur.models import Laboratorio, Producto, Lote, Merma
from farmasur.serializers.inventario.serializers import (
    LaboratorioSerializer,
    ProductoListSerializer,
    ProductoDetailSerializer,
    LoteListSerializer,
    LoteDetailSerializer,
    MermaSerializer,
)
from farmasur.services.inventario.services import LoteService, StockService, MermaService
from farmasur.permissions.inventario.permissions import PuedeVerInventario, PuedeModificarInventario


class LaboratorioViewSet(viewsets.ModelViewSet):
    """CRUD para laboratorios."""
    queryset = Laboratorio.objects.all()
    serializer_class = LaboratorioSerializer
    permission_classes = [IsAuthenticated, PuedeVerInventario]
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ['nombre', 'pais']
    ordering_fields = ['nombre', 'fecha_creacion']
    ordering = ['nombre']
    
    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated, PuedeModificarInventario]
        return super().get_permissions()


class ProductoViewSet(viewsets.ModelViewSet):
    """CRUD para productos."""
    queryset = Producto.objects.select_related('laboratorio').all()
    permission_classes = [IsAuthenticated, PuedeVerInventario]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['laboratorio', 'activo']
    search_fields = ['nombre_comercial', 'sku_codigo_barra', 'principio_activo']
    ordering_fields = ['nombre_comercial', 'precio_clp', 'fecha_creacion']
    ordering = ['nombre_comercial']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductoListSerializer
        return ProductoDetailSerializer
    
    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated, PuedeModificarInventario]
        return super().get_permissions()


class LoteViewSet(viewsets.ModelViewSet):
    """CRUD para lotes con soporte FEFO."""
    queryset = Lote.objects.select_related('producto__laboratorio').all()
    permission_classes = [IsAuthenticated, PuedeVerInventario]
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_fields = ['producto', 'activo']
    ordering_fields = ['fecha_vencimiento', 'fecha_creacion']
    ordering = ['fecha_vencimiento']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LoteListSerializer
        return LoteDetailSerializer
    
    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated, PuedeModificarInventario]
        return super().get_permissions()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, PuedeVerInventario])
    def fefo(self, request):
        """Retorna lotes ordenados por FEFO (vencimiento mÃ¡s prÃ³ximo primero)."""
        producto_id = request.query_params.get('producto_id')
        
        if not producto_id:
            return Response(
                {'error': 'Se requiere producto_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            lotes = LoteService.obtener_lotes_fefo(producto_id=producto_id)
            serializer = self.get_serializer(lotes, many=True)
            return Response(serializer.data)
        except Producto.DoesNotExist:
            return Response(
                {'error': 'Producto no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, PuedeModificarInventario])
    def dispensar_fefo(self, request):
        """Dispensa cantidad de un producto usando algoritmo FEFO."""
        producto_id = request.data.get('producto_id')
        cantidad = request.data.get('cantidad')
        
        if not producto_id or not cantidad:
            return Response(
                {'error': 'Se requiere producto_id y cantidad'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            resultado = LoteService.dispensar_lote_fefo(
                producto_id=int(producto_id),
                cantidad=int(cantidad),
                usuario=request.user
            )
            return Response(resultado, status=status.HTTP_200_OK)
        except (ValueError, Producto.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, PuedeVerInventario])
    def stock_actual(self, request):
        """Retorna stock actual por producto."""
        producto_id = request.query_params.get('producto_id')
        
        if producto_id:
            try:
                stock = StockService.calcular_stock_total(producto_id=int(producto_id))
                return Response({'producto_id': producto_id, 'stock_total': stock})
            except Producto.DoesNotExist:
                return Response(
                    {'error': 'Producto no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        stocks = StockService.obtener_stock_todos_productos()
        return Response(stocks)


class MermaViewSet(viewsets.ModelViewSet):
    """CRUD para mermas (pÃ©rdidas de medicamentos)."""
    queryset = Merma.objects.select_related('lote__producto', 'aprobado_por').all()
    serializer_class = MermaSerializer
    permission_classes = [IsAuthenticated, PuedeModificarInventario]
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_fields = ['lote', 'razon']
    ordering_fields = ['fecha_registro', 'cantidad']
    ordering = ['-fecha_registro']
    
    def perform_create(self, serializer):
        """Registra merma y actualiza stock del lote."""
        from django.db import transaction
        from rest_framework.exceptions import ValidationError
        try:
            with transaction.atomic():
                merma = serializer.save()
                MermaService.registrar_merma(merma)
        except ValueError as e:
            raise ValidationError({'cantidad': str(e)})
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, PuedeVerInventario])
    def reporte_mermas(self, request):
        """Reporte de mermas por perÃ­odo o filtro."""
        from datetime import date, timedelta
        
        dias = request.query_params.get('dias', 30)
        fecha_desde = date.today() - timedelta(days=int(dias))
        
        mermas = Merma.objects.filter(
            fecha_registro__date__gte=fecha_desde
        ).select_related('lote__producto', 'aprobado_por')
        
        total_mermas = sum(m.cantidad for m in mermas)
        por_motivo = {}
        
        for merma in mermas:
            motivo = merma.get_razon_display()
            if motivo not in por_motivo:
                por_motivo[motivo] = {'cantidad': 0, 'valor_aproximado': 0}
            por_motivo[motivo]['cantidad'] += merma.cantidad
            por_motivo[motivo]['valor_aproximado'] += (
                merma.cantidad * merma.lote.producto.precio_clp
            )
        
        return Response({
            'fecha_desde': fecha_desde,
            'fecha_hasta': date.today(),
            'total_unidades': total_mermas,
            'por_motivo': por_motivo,
        })
