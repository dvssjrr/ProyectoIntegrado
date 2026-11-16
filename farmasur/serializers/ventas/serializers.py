"""
Serializadores para la app ventas.
Validación y representación de datos de API.
"""
from rest_framework import serializers
from farmasur.models import CajaDiaria, POS, ConvenioIsapre, Comprobante, Usuario


class CajaDiariaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de cajas."""
    operario_nombre = serializers.CharField(source='operario.nombre_completo', read_only=True)
    
    class Meta:
        model = CajaDiaria
        fields = [
            'id', 'caja_id', 'fecha', 'turno', 'operario_nombre',
            'monto_inicial', 'total_ventas', 'estado', 'hora_apertura'
        ]
        read_only_fields = ['hora_apertura']


class CajaDiariaDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de caja."""
    operario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())
    
    class Meta:
        model = CajaDiaria
        fields = [
            'id', 'caja_id', 'fecha', 'turno', 'operario',
            'monto_inicial', 'monto_cierre', 'diferencia',
            'total_ventas', 'total_descuentos', 'estado',
            'hora_apertura', 'hora_cierre', 'notas', 'datos_cierre'
        ]
        read_only_fields = ['fecha', 'hora_apertura', 'hora_cierre']


class POSListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de ventas."""
    operario_nombre = serializers.CharField(source='operario.nombre_completo', read_only=True)
    
    class Meta:
        model = POS
        fields = [
            'id', 'folio', 'fecha_venta', 'operario_nombre',
            'nombre_cliente', 'tipo_comprobante', 'total'
        ]
        read_only_fields = ['fecha_venta']


class POSDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de venta."""
    operario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())
    caja = serializers.PrimaryKeyRelatedField(queryset=CajaDiaria.objects.all())
    
    class Meta:
        model = POS
        fields = [
            'id', 'caja', 'folio', 'fecha_venta', 'operario',
            'rut_cliente', 'nombre_cliente', 'tipo_comprobante',
            'subtotal', 'descuento_total', 'total',
            'convenio_aplicado', 'porcentaje_descuento_convenio',
            'requiere_receta_retenida', 'receta_retenida',
            'requiere_unidosis', 'items', 'notas', 'comprobante_impreso'
        ]
        read_only_fields = ['fecha_venta']


class ConvenioIsapreSerializer(serializers.ModelSerializer):
    """Serializer para convenios Isapre."""
    
    class Meta:
        model = ConvenioIsapre
        fields = [
            'id', 'nombre', 'descripcion', 'porcentaje_descuento',
            'medicamentos_excluidos', 'monto_maximo_descuento',
            'requiere_autorizacion_qf', 'activo', 'fecha_creacion',
            'fecha_ultima_modificacion'
        ]
        read_only_fields = ['fecha_creacion', 'fecha_ultima_modificacion']


class ComprobanteListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de comprobantes."""
    
    class Meta:
        model = Comprobante
        fields = [
            'id', 'tipo', 'folio_comprobante', 'nombre_receptor',
            'fecha_emision', 'total', 'estado'
        ]
        read_only_fields = ['fecha_emision']


class ComprobanteDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de comprobante."""
    
    class Meta:
        model = Comprobante
        fields = [
            'id', 'venta_pos', 'tipo', 'folio_comprobante',
            'rut_receptor', 'nombre_receptor', 'giro_receptor',
            'direccion_receptor', 'fecha_emision', 'fecha_vencimiento',
            'neto', 'iva', 'total', 'rut_emisor', 'nombre_emisor',
            'archivo_pdf', 'estado', 'notas'
        ]
        read_only_fields = ['fecha_emision']
