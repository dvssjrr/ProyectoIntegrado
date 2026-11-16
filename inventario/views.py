"""
Vistas (ViewSets) para la app inventario.
Endpoints API REST con DRF.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters

from .models import Laboratorio, Producto, Lote, Merma
from .serializers import (
    LaboratorioSerializer,
    ProductoListSerializer,
    ProductoDetailSerializer,
    LoteListSerializer,
    LoteDetailSerializer,
    MermaSerializer,
)
from .services import LoteService, StockService, MermaService
from .permissions import PuedeVerInventario, PuedeModificarInventario


class LaboratorioViewSet(viewsets.ModelViewSet):
    """CRUD para laboratorios."""
    queryset = Laboratorio.objects.all()
    serializer_class = LaboratorioSerializer
    permission_classes = [IsAuthenticated, PuedeVerInventario]
    filter_backends = [drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ['nombre', 'codigo']
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
    search_fields = ['nombre', 'codigo', 'principio_activo']
    ordering_fields = ['nombre', 'precio_unitario', 'fecha_creacion']
    ordering = ['nombre']
    
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
        """Retorna lotes ordenados por FEFO (vencimiento más próximo primero)."""
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
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, PuedeModificarInventario])
    def dispensar_fefo(self, request):
        """Dispensa cantidad de un producto usando algoritmo FEFO."""
        cantidad = request.data.get('cantidad')
        
        if not cantidad:
            return Response(
                {'error': 'Se requiere cantidad'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            resultado = LoteService.dispensar_lote_fefo(
                producto_id=self.get_object().producto.id,
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
    """CRUD para mermas (pérdidas de medicamentos)."""
    queryset = Merma.objects.select_related('lote__producto', 'responsable').all()
    serializer_class = MermaSerializer
    permission_classes = [IsAuthenticated, PuedeModificarInventario]
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_fields = ['lote', 'motivo']
    ordering_fields = ['fecha_creacion', 'cantidad']
    ordering = ['-fecha_creacion']
    
    def perform_create(self, serializer):
        """Registra merma y actualiza stock del lote."""
        merma = serializer.save(responsable=self.request.user)
        MermaService.registrar_merma(merma)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, PuedeVerInventario])
    def reporte_mermas(self, request):
        """Reporte de mermas por período o filtro."""
        from datetime import date, timedelta
        
        dias = request.query_params.get('dias', 30)
        fecha_desde = date.today() - timedelta(days=int(dias))
        
        mermas = Merma.objects.filter(
            fecha_creacion__gte=fecha_desde
        ).select_related('lote__producto', 'responsable')
        
        total_mermas = sum(m.cantidad for m in mermas)
        por_motivo = {}
        
        for merma in mermas:
            motivo = merma.get_motivo_display()
            if motivo not in por_motivo:
                por_motivo[motivo] = {'cantidad': 0, 'valor_aproximado': 0}
            por_motivo[motivo]['cantidad'] += merma.cantidad
            por_motivo[motivo]['valor_aproximado'] += (
                merma.cantidad * merma.lote.producto.precio_unitario
            )
        
        return Response({
            'fecha_desde': fecha_desde,
            'fecha_hasta': date.today(),
            'total_unidades': total_mermas,
            'por_motivo': por_motivo,
        })
