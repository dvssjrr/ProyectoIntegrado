from django.contrib import admin
from .models import Laboratorio, Producto, Lote, RecepcionProveedor, Merma

@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pais', 'email', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'pais', 'fecha_creacion')
    search_fields = ('nombre', 'email', 'contacto')
    ordering = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre_comercial', 'sku_codigo_barra', 'laboratorio', 'condicion_venta', 'precio_clp', 'stock_minimo_vitrina', 'activo')
    list_filter = ('activo', 'categoria', 'condicion_venta', 'laboratorio', 'requiere_cadena_frio')
    search_fields = ('nombre_comercial', 'sku_codigo_barra', 'principio_activo')
    readonly_fields = ('fecha_creacion', 'fecha_ultima_modificacion', 'stock_total_vitrina', 'stock_total_bodega')
    ordering = ('nombre_comercial',)
    
    fieldsets = (
        ('Información Básica', {'fields': ('sku_codigo_barra', 'nombre_comercial', 'principio_activo')}),
        ('Clasificación', {'fields': ('categoria', 'laboratorio', 'condicion_venta', 'presentacion')}),
        ('Precios y Stock', {'fields': ('precio_clp', 'stock_minimo_vitrina', 'stock_total_vitrina', 'stock_total_bodega')}),
        ('Almacenamiento', {'fields': ('requiere_cadena_frio',)}),
        ('Estado', {'fields': ('activo', 'fecha_creacion', 'fecha_ultima_modificacion')}),
    )

@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('producto', 'codigo_lote', 'fecha_vencimiento', 'estado_fefo', 'stock_vitrina', 'stock_bodega', 'bloqueado_vencimiento')
    list_filter = ('bloqueado_vencimiento', 'fecha_vencimiento', 'activo')
    search_fields = ('producto__nombre_comercial', 'codigo_lote')
    readonly_fields = ('fecha_creacion', 'fecha_ultima_modificacion', 'dias_para_vencer', 'estado_fefo')
    ordering = ('fecha_vencimiento',)
    
    fieldsets = (
        ('Producto y Lote', {'fields': ('producto', 'codigo_lote', 'fecha_vencimiento')}),
        ('Stock', {'fields': ('stock_vitrina', 'stock_bodega')}),
        ('Costo', {'fields': ('costo_compra',)}),
        ('Estado', {'fields': ('bloqueado_vencimiento', 'dias_para_vencer', 'estado_fefo', 'activo', 'fecha_creacion', 'fecha_ultima_modificacion')}),
    )

@admin.register(RecepcionProveedor)
class RecepcionProveedorAdmin(admin.ModelAdmin):
    list_display = ('numero_orden_compra', 'laboratorio', 'estado', 'fecha_recepcion', 'fecha_validacion')
    list_filter = ('estado', 'laboratorio', 'fecha_recepcion')
    search_fields = ('numero_orden_compra', 'numero_factura_proveedor', 'laboratorio__nombre')
    readonly_fields = ('fecha_recepcion', 'fecha_validacion')
    ordering = ('-fecha_recepcion',)

@admin.register(Merma)
class MermaAdmin(admin.ModelAdmin):
    list_display = ('lote', 'cantidad', 'razon', 'aprobado_por', 'fecha_registro', 'fecha_aprobacion')
    list_filter = ('razon', 'fecha_registro', 'aprobado_por')
    search_fields = ('lote__producto__nombre_comercial', 'descripcion')
    readonly_fields = ('fecha_registro', 'fecha_aprobacion')
    ordering = ('-fecha_registro',)

