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
        fields = ['id', 'nombre', 'pais', 'telefono', 'email', 'contacto', 'activo', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']


class ProductoListSerializer(serializers.ModelSerializer):
    """Serializer para listar productos (datos básicos)."""
    laboratorio_nombre = serializers.CharField(source='laboratorio.nombre', read_only=True)
    stock_vitrina = serializers.IntegerField(source='stock_total_vitrina', read_only=True)
    stock_bodega = serializers.IntegerField(source='stock_total_bodega', read_only=True)
    
    class Meta:
        model = Producto
        fields = ['id', 'sku_codigo_barra', 'nombre_comercial', 'presentacion', 'laboratorio',
                  'laboratorio_nombre', 'precio_clp', 'stock_vitrina', 'stock_bodega', 'activo']
        read_only_fields = ['id', 'stock_vitrina', 'stock_bodega']


class ProductoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para Producto."""
    laboratorio_nombre = serializers.CharField(source='laboratorio.nombre', read_only=True)
    stock_vitrina = serializers.IntegerField(source='stock_total_vitrina', read_only=True)
    stock_bodega = serializers.IntegerField(source='stock_total_bodega', read_only=True)
    
    class Meta:
        model = Producto
        fields = '__all__'
        read_only_fields = ['id', 'fecha_creacion', 'fecha_ultima_modificacion']


class LoteListSerializer(serializers.ModelSerializer):
    """Serializer para listar lotes."""
    producto_nombre = serializers.CharField(source='producto.nombre_comercial', read_only=True)
    estado_fefo = serializers.CharField(read_only=True)
    dias_para_vencer = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Lote
        fields = ['id', 'codigo_lote', 'producto', 'producto_nombre', 'stock_vitrina', 'stock_bodega',
                  'fecha_vencimiento', 'estado_fefo', 'dias_para_vencer']
        read_only_fields = ['id', 'estado_fefo', 'dias_para_vencer']


class LoteDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para Lote."""
    producto_nombre = serializers.CharField(source='producto.nombre_comercial', read_only=True)
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
    
    class Meta:
        model = RecepcionProveedor
        fields = ['id', 'numero_orden_compra', 'numero_factura_proveedor', 'laboratorio', 'estado',
                  'fecha_recepcion', 'datos_cubeta', 'notas', 'fecha_validacion']
        read_only_fields = ['id', 'fecha_recepcion', 'fecha_validacion']


class MermaSerializer(serializers.ModelSerializer):
    """Serializer para Merma (pérdida de medicamentos)."""
    codigo_lote = serializers.CharField(source='lote.codigo_lote', read_only=True)
    producto_nombre = serializers.CharField(source='lote.producto.nombre_comercial', read_only=True)
    
    class Meta:
        model = Merma
        fields = ['id', 'lote', 'codigo_lote', 'producto_nombre', 'cantidad', 'razon',
                  'descripcion', 'aprobado_por', 'fecha_registro', 'fecha_aprobacion']
        read_only_fields = ['id', 'fecha_registro', 'aprobado_por', 'fecha_aprobacion']
