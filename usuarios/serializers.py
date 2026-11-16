"""
Serializers para la app usuarios.
Validación y representación de datos de Usuario para API REST.
"""
from rest_framework import serializers
from .models import Usuario, LogAuditoria
from .validators import validar_rut_chileno


class UsuarioListSerializer(serializers.ModelSerializer):
    """Serializer para listar usuarios (datos básicos)."""
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre_completo', 'rut', 'rol', 'rol_display', 'activo', 'email']
        read_only_fields = ['id', 'fecha_creacion', 'fecha_ultima_modificacion']


class UsuarioDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para Usuario (crear/actualizar)."""
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    rut = serializers.CharField(validators=[validar_rut_chileno])
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'nombre_completo', 'rut', 'rol',
            'rol_display', 'activo', 'fecha_creacion', 'fecha_ultima_modificacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_ultima_modificacion']
    
    def validate_rut(self, value):
        """Valida que el RUT sea único."""
        instance = self.instance
        if Usuario.objects.filter(rut=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Este RUT ya está registrado.")
        return value


class LogAuditoriaSerializer(serializers.ModelSerializer):
    """Serializer para registros de auditoría (solo lectura)."""
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = LogAuditoria
        fields = [
            'id', 'usuario', 'usuario_username', 'accion', 'tabla_afectada',
            'descripcion', 'timestamp', 'hash_sha256', 'hash_anterior'
        ]
        read_only_fields = '__all__'
