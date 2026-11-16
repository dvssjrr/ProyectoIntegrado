"""
Serializadores para la app recetas.
Validación y representación de datos de API.
"""
from rest_framework import serializers
from .models import Receta, RecetaRetenidaISP, UnidosisAsistencial
from usuarios.models import Usuario


class RecetaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de recetas."""
    aprobado_por_nombre = serializers.CharField(source='aprobado_por.nombre_completo', read_only=True)
    dias_vigencia = serializers.SerializerMethodField()
    
    class Meta:
        model = Receta
        fields = [
            'id', 'folio', 'rut_paciente', 'nombre_paciente',
            'estado', 'fecha_emision', 'fecha_aprobacion',
            'aprobado_por_nombre', 'dias_vigencia', 'fecha_registro'
        ]
        read_only_fields = ['fecha_registro']
    
    def get_dias_vigencia(self, obj):
        return obj.dias_desde_emision


class RecetaDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de receta."""
    aprobado_por = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.filter(rol=Usuario.Rol.FARMACEUTICO),
        required=False,
        allow_null=True
    )
    dias_vigencia = serializers.SerializerMethodField()
    esta_vigente = serializers.SerializerMethodField()
    
    class Meta:
        model = Receta
        fields = [
            'id', 'folio', 'rut_paciente', 'nombre_paciente',
            'rut_medico', 'nombre_medico', 'fecha_emision',
            'estado', 'medicamentos', 'notas_prescriptor',
            'fecha_aprobacion', 'aprobado_por', 'fecha_dispensacion',
            'razon_rechazo', 'fecha_registro', 'datos_adicionales',
            'dias_vigencia', 'esta_vigente'
        ]
        read_only_fields = ['fecha_registro', 'fecha_aprobacion', 'fecha_dispensacion']
    
    def get_dias_vigencia(self, obj):
        return obj.dias_desde_emision
    
    def get_esta_vigente(self, obj):
        return obj.esta_vigente


class RecetaRetenidaISPSerializer(serializers.ModelSerializer):
    """Serializer para recetas retenidas ISP."""
    receta_folio = serializers.CharField(source='receta.folio', read_only=True)
    dispensado_por_nombre = serializers.CharField(source='dispensado_por.nombre_completo', read_only=True)
    
    class Meta:
        model = RecetaRetenidaISP
        fields = [
            'id', 'receta', 'receta_folio', 'numero_serie_carnet_paciente',
            'numero_serie_carnet_medico', 'folio_isp', 'fecha_dispensacion',
            'dispensado_por', 'dispensado_por_nombre', 'hash_sha256', 'hash_anterior',
            'datos_receta_jsonb'
        ]
        read_only_fields = ['fecha_dispensacion', 'hash_sha256', 'hash_anterior']


class UnidosisAsistencialListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de unidosis."""
    solicitado_por_nombre = serializers.CharField(source='solicitado_por.nombre_completo', read_only=True)
    dispensado_por_nombre = serializers.CharField(source='dispensado_por.nombre_completo', read_only=True)
    
    class Meta:
        model = UnidosisAsistencial
        fields = [
            'id', 'folio', 'rut_paciente', 'nombre_paciente',
            'estado', 'fecha_solicitud', 'fecha_dispensacion',
            'solicitado_por_nombre', 'dispensado_por_nombre'
        ]
        read_only_fields = ['fecha_solicitud', 'fecha_dispensacion']


class UnidosisAsistencialDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de unidosis."""
    solicitado_por = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        required=False
    )
    dispensado_por = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = UnidosisAsistencial
        fields = [
            'id', 'folio', 'numero_serie_carnet_paciente', 'rut_paciente',
            'nombre_paciente', 'medicamentos', 'estado', 'observaciones',
            'solicitado_por', 'dispensado_por', 'fecha_solicitud', 'fecha_dispensacion'
        ]
        read_only_fields = ['fecha_solicitud', 'fecha_dispensacion']
