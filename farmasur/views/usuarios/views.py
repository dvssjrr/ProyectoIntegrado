"""
Views para la app usuarios.
Endpoints API REST y coordinación de solicitudes.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from farmasur.models import Usuario, LogAuditoria
from farmasur.serializers.usuarios.serializers import UsuarioListSerializer, UsuarioDetailSerializer, LogAuditoriaSerializer
from farmasur.permissions.usuarios.permissions import EsAdmin, EsAdminOLectura, es_admin
from farmasur.services.usuarios.services import UsuarioService, LogAuditoriaService


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Usuarios.
    - GET /api/usuarios/: listar usuarios
    - POST /api/usuarios/: crear usuario (solo admin)
    - GET /api/usuarios/{id}/: obtener usuario
    - PUT /api/usuarios/{id}/: actualizar usuario
    - DELETE /api/usuarios/{id}/: eliminar usuario (solo admin)
    """
    queryset = Usuario.objects.all().order_by('nombre_completo')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UsuarioListSerializer
        return UsuarioDetailSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [EsAdmin]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [EsAdminOLectura]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [perm() for perm in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """Crear un nuevo usuario."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        usuario = UsuarioService.crear_usuario(
            username=serializer.validated_data['username'],
            email=serializer.validated_data.get('email', ''),
            nombre_completo=serializer.validated_data['nombre_completo'],
            rut=serializer.validated_data['rut'],
            rol=serializer.validated_data['rol'],
            password=request.data.get('password')
        )
        
        return Response(
            UsuarioDetailSerializer(usuario).data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """Actualizar un usuario."""
        usuario = self.get_object()
        
        # Actualizar con auditoría
        usuario_actualizado = UsuarioService.actualizar_usuario(usuario.pk, **request.data)
        
        return Response(
            UsuarioDetailSerializer(usuario_actualizado).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cambiar_contrasena(self, request, pk=None):
        """Cambiar contraseña de un usuario."""
        usuario = self.get_object()
        
        # Verificar que solo admin o el usuario mismo pueda cambiar contraseña
        if usuario != request.user and not es_admin(request.user):
            return Response(
                {'detail': 'No tienes permiso para cambiar la contraseña de otro usuario.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        nueva_contrasena = request.data.get('nueva_contrasena')
        if not nueva_contrasena:
            return Response(
                {'detail': 'Debes proporcionar una nueva contraseña.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        UsuarioService.cambiar_contrasena(usuario.pk, nueva_contrasena)
        
        return Response(
            {'detail': 'Contraseña cambiada exitosamente.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], permission_classes=[EsAdmin])
    def por_rol(self, request):
        """Obtener usuarios filtrados por rol."""
        rol = request.query_params.get('rol')
        if not rol:
            return Response(
                {'detail': 'Proporciona el parámetro rol.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        usuarios = UsuarioService.obtener_usuarios_por_rol(rol)
        serializer = UsuarioListSerializer(usuarios, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class AuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar registros de auditoría (solo lectura).
    - GET /api/auditoria/: listar registros de auditoría
    - GET /api/auditoria/{id}/: obtener registro específico
    """
    queryset = LogAuditoria.objects.all().order_by('-timestamp')
    serializer_class = LogAuditoriaSerializer
    permission_classes = [EsAdmin]
    
    @action(detail=False, methods=['get'])
    def por_tipo_evento(self, request):
        """Obtener auditoría filtrada por tipo de evento."""
        tipo_evento = request.query_params.get('tipo_evento')
        if not tipo_evento:
            return Response(
                {'detail': 'Proporciona el parámetro tipo_evento.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        registros = LogAuditoriaService.obtener_historial(tipo_evento=tipo_evento)
        serializer = LogAuditoriaSerializer(registros, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def validar_integridad(self, request, pk=None):
        """Validar la integridad de la cadena SHA-256 desde un registro."""
        log = get_object_or_404(LogAuditoria, pk=pk)
        es_integro = LogAuditoriaService.validar_integridad_cadena(pk)
        
        return Response({
            'log_id': pk,
            'integridad': es_integro,
            'timestamp': log.timestamp,
            'tipo_evento': log.tipo_evento,
            'descripcion': log.descripcion
        })

