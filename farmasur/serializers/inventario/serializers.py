"""
Serializers para la app inventario.
Validación y representación de datos de medicamentos, lotes, etc.
"""
from rest_framework import serializers
from farmasur.models import Laboratorio, Producto, Lote, RecepcionProveedor, Merma


class LaboratorioSerializer(serializers.ModelSerializer):
    """Serializer para Laboratorio."""
    
    class Meta:
        model = Laboratorio
        fields = ['id', 'nombre', 'descripcion', 'contacto', 'activo', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']


class ProductoListSerializer(serializers.ModelSerializer):
    """Serializer para listar productos (datos básicos)."""
    laboratorio_nombre = serializers.CharField(source='laboratorio.nombre', read_only=True)
    stock_actual = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'codigo', 'laboratorio', 'laboratorio_nombre', 
                 'stock_actual', 'precio_venta_lote', 'activo']
        read_only_fields = ['id', 'stock_actual']


class ProductoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para Producto."""
    laboratorio_nombre = serializers.CharField(source='laboratorio.nombre', read_only=True)
    stock_vitrina = serializers.IntegerField(read_only=True)
    stock_bodega = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Producto
        fields = '__all__'
        read_only_fields = ['id', 'fecha_creacion', 'fecha_ultima_modificacion', 'stock_vitrina', 'stock_bodega']


class LoteListSerializer(serializers.ModelSerializer):
    """Serializer para listar lotes."""
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    estado_fefo = serializers.CharField(read_only=True)
    dias_para_vencer = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Lote
        fields = ['id', 'numero_lote', 'producto', 'producto_nombre', 'cantidad_total',
                 'fecha_vencimiento', 'estado_fefo', 'dias_para_vencer', 'ubicacion']
        read_only_fields = ['id', 'estado_fefo', 'dias_para_vencer']


class LoteDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para Lote."""
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    estado_fefo = serializers.CharField(read_only=True)
    dias_para_vencer = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Lote
        fields = '__all__'
        read_only_fields = ['id', 'fecha_creacion', 'estado_fefo', 'dias_para_vencer']
    
    def validate(self, data):
        """Validar que fecha_vencimiento sea válida."""
        from datetime import date
        if data.get('fecha_vencimiento') and data['fecha_vencimiento'] < date.today():
            raise serializers.ValidationError("La fecha de vencimiento no puede ser en el pasado.")
        return data


class RecepcionProveedorSerializer(serializers.ModelSerializer):
    """Serializer para Recepción de Proveedor."""
    lotes_creados = LoteDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = RecepcionProveedor
        fields = ['id', 'proveedor', 'fecha_recepcion', 'numero_factura', 'descripcion', 
                 'cantidad_cajas', 'lotes_creados', 'timestamp']
        read_only_fields = ['id', 'timestamp', 'lotes_creados']


class MermaSerializer(serializers.ModelSerializer):
    """Serializer para Merma (pérdida de medicamentos)."""
    lote_numero = serializers.CharField(source='lote.numero_lote', read_only=True)
    producto_nombre = serializers.CharField(source='lote.producto.nombre', read_only=True)
    
    class Meta:
        model = Merma
        fields = ['id', 'lote', 'lote_numero', 'producto_nombre', 'cantidad', 
                 'motivo', 'timestamp', 'responsable']
        read_only_fields = ['id', 'timestamp']
