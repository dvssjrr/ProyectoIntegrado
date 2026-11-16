"""
Vistas (ViewSets) para la app recetas.
Endpoints API REST con DRF.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters

from .models import Receta, RecetaRetenidaISP, UnidosisAsistencial
from .serializers import (
    RecetaListSerializer,
    RecetaDetailSerializer,
    RecetaRetenidaISPSerializer,
    UnidosisAsistencialListSerializer,
    UnidosisAsistencialDetailSerializer,
)
from .services import RecetaService, RecetaRetenidaISPService, UnidosisAsistencialService
from .permissions import PuedeVerRecetas, PuedeModificarRecetas, SoloFarmaceutico


class RecetaViewSet(viewsets.ModelViewSet):
    """CRUD para recetas médicas."""
    queryset = Receta.objects.all()
    serializer_class = RecetaDetailSerializer
    permission_classes = [IsAuthenticated, PuedeVerRecetas]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['estado', 'rut_paciente', 'rut_medico']
    search_fields = ['folio', 'nombre_paciente', 'nombre_medico']
    ordering_fields = ['fecha_emision', 'fecha_registro']
    ordering = ['-fecha_registro']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RecetaListSerializer
        return RecetaDetailSerializer
    
    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated, PuedeModificarRecetas]
        return super().get_permissions()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, SoloFarmaceutico])
    def aprobar(self, request, pk=None):
        """Aprueba una receta (solo farmacéuticos)."""
        try:
            receta = RecetaService.aprobar_receta(pk, request.user)
            serializer = self.get_serializer(receta)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (ValueError, Receta.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, PuedeModificarRecetas])
    def rechazar(self, request, pk=None):
        """Rechaza una receta."""
        razon = request.data.get('razon_rechazo', 'Rechazada sin especificar motivo')
        
        try:
            receta = RecetaService.rechazar_receta(pk, razon)
            serializer = self.get_serializer(receta)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (ValueError, Receta.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, SoloFarmaceutico])
    def dispensar(self, request, pk=None):
        """Dispensa una receta (solo farmacéuticos)."""
        try:
            receta = RecetaService.dispensar_receta(pk)
            serializer = self.get_serializer(receta)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (ValueError, Receta.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, PuedeVerRecetas])
    def vigentes(self, request):
        """Retorna recetas vigentes (< 30 días)."""
        recetas = RecetaService.listar_recetas_vigentes()
        serializer = self.get_serializer(recetas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, PuedeVerRecetas])
    def vencidas(self, request):
        """Retorna recetas vencidas (> 30 días)."""
        recetas = RecetaService.listar_recetas_vencidas()
        serializer = self.get_serializer(recetas, many=True)
        return Response(serializer.data)


class RecetaRetenidaISPViewSet(viewsets.ReadOnlyModelViewSet):
    """Vista de solo lectura para recetas retenidas ISP."""
    queryset = RecetaRetenidaISP.objects.all()
    serializer_class = RecetaRetenidaISPSerializer
    permission_classes = [IsAuthenticated, SoloFarmaceutico]
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_fields = ['receta']
    ordering_fields = ['fecha_dispensacion']
    ordering = ['-fecha_dispensacion']
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, SoloFarmaceutico])
    def validar_integridad(self, request, pk=None):
        """Valida integridad del encadenamiento de hash."""
        try:
            receta_retenida = self.get_object()
            es_valida = RecetaRetenidaISPService.validar_integridad(pk)
            return Response({
                'folio_isp': receta_retenida.folio_isp,
                'integridad_valida': es_valida
            })
        except RecetaRetenidaISP.DoesNotExist:
            return Response(
                {'error': 'Receta retenida no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )


class UnidosisAsistencialViewSet(viewsets.ModelViewSet):
    """CRUD para unidosis asistencial."""
    queryset = UnidosisAsistencial.objects.all()
    serializer_class = UnidosisAsistencialDetailSerializer
    permission_classes = [IsAuthenticated, PuedeModificarRecetas]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['estado', 'rut_paciente']
    search_fields = ['folio', 'nombre_paciente']
    ordering_fields = ['fecha_solicitud', 'fecha_dispensacion']
    ordering = ['-fecha_solicitud']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UnidosisAsistencialListSerializer
        return UnidosisAsistencialDetailSerializer
    
    def perform_create(self, serializer):
        """Registra usuario solicitante."""
        serializer.save(solicitado_por=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, PuedeModificarRecetas])
    def preparar(self, request, pk=None):
        """Marca unidosis como preparada."""
        try:
            unidosis = UnidosisAsistencialService.preparar_unidosis(pk)
            serializer = self.get_serializer(unidosis)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (ValueError, UnidosisAsistencial.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, PuedeModificarRecetas])
    def dispensar(self, request, pk=None):
        """Dispensa unidosis."""
        try:
            unidosis = UnidosisAsistencialService.dispensar_unidosis(pk, request.user)
            serializer = self.get_serializer(unidosis)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (ValueError, UnidosisAsistencial.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, PuedeModificarRecetas])
    def cancelar(self, request, pk=None):
        """Cancela una unidosis."""
        observaciones = request.data.get('observaciones', '')
        
        try:
            unidosis = UnidosisAsistencialService.cancelar_unidosis(pk, observaciones)
            serializer = self.get_serializer(unidosis)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (ValueError, UnidosisAsistencial.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
