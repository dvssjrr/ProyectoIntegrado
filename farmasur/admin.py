"""
Administración centralizada de la aplicación Farmasur.
"""
from django.contrib import admin

# Importar modelos
from farmasur.models.usuarios.models import Usuario, LogAuditoria
from farmasur.models.inventario.models import (
    Laboratorio,
    Producto,
    Lote,
    RecepcionProveedor,
    Merma,
)
from farmasur.models.recetas.models import Receta, RecetaRetenidaISP, UnidosisAsistencial
from farmasur.models.ventas.models import CajaDiaria, POS, ConvenioIsapre, Comprobante

# ============================================================================
# USUARIOS
# ============================================================================

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'nombre_completo', 'rol', 'activo', 'fecha_creacion')
    list_filter = ('rol', 'activo', 'fecha_creacion')
    search_fields = ('username', 'email', 'nombre_completo')
    readonly_fields = ('fecha_creacion', 'fecha_ultima_modificacion')


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo_evento', 'timestamp')
    list_filter = ('tipo_evento', 'timestamp')
    search_fields = ('usuario__username', 'descripcion')
    readonly_fields = ('hash_sha256', 'hash_anterior', 'timestamp')


# ============================================================================
# INVENTARIO
# ============================================================================

@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pais', 'email', 'activo', 'fecha_creacion')
    list_filter = ('pais', 'activo', 'fecha_creacion')
    search_fields = ('nombre', 'email')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku_codigo_barra', 'nombre_comercial', 'principio_activo', 'condicion_venta', 'precio_clp')
    list_filter = ('presentacion', 'condicion_venta', 'activo')
    search_fields = ('sku_codigo_barra', 'nombre_comercial', 'principio_activo')


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('codigo_lote', 'producto', 'fecha_vencimiento', 'stock_vitrina', 'stock_bodega', 'activo')
    list_filter = ('fecha_vencimiento', 'bloqueado_vencimiento')
    search_fields = ('codigo_lote', 'producto__nombre_comercial')


@admin.register(RecepcionProveedor)
class RecepcionProveedorAdmin(admin.ModelAdmin):
    list_display = ('numero_orden_compra', 'laboratorio', 'fecha_recepcion', 'estado')
    list_filter = ('fecha_recepcion', 'estado')
    search_fields = ('numero_orden_compra', 'laboratorio__nombre')


@admin.register(Merma)
class MermaAdmin(admin.ModelAdmin):
    list_display = ('id', 'lote', 'cantidad', 'fecha_registro')
    list_filter = ('fecha_registro',)
    search_fields = ('lote__codigo_lote',)


# ============================================================================
# RECETAS
# ============================================================================

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ('folio', 'nombre_paciente', 'nombre_medico', 'fecha_emision', 'estado')
    list_filter = ('estado', 'fecha_emision')
    search_fields = ('folio', 'nombre_paciente', 'nombre_medico')


@admin.register(RecetaRetenidaISP)
class RecetaRetenidaISPAdmin(admin.ModelAdmin):
    list_display = ('receta', 'fecha_dispensacion')
    list_filter = ('fecha_dispensacion',)
    search_fields = ('receta__folio',)


@admin.register(UnidosisAsistencial)
class UnidosisAsistencialAdmin(admin.ModelAdmin):
    list_display = ('folio', 'nombre_paciente', 'estado', 'fecha_solicitud')
    list_filter = ('estado', 'fecha_solicitud')
    search_fields = ('folio', 'nombre_paciente')


# ============================================================================
# VENTAS
# ============================================================================

@admin.register(CajaDiaria)
class CajaDiariaAdmin(admin.ModelAdmin):
    list_display = ('caja_id', 'fecha', 'monto_inicial', 'total_ventas', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('caja_id',)


@admin.register(POS)
class POSAdmin(admin.ModelAdmin):
    list_display = ('folio', 'fecha_venta', 'total', 'nombre_cliente', 'caja')
    list_filter = ('fecha_venta',)
    search_fields = ('folio', 'nombre_cliente')


@admin.register(ConvenioIsapre)
class ConvenioIsapreAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'porcentaje_descuento', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)


@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ('folio_comprobante', 'venta_pos', 'tipo', 'fecha_emision', 'total')
    list_filter = ('tipo', 'fecha_emision')
    search_fields = ('folio_comprobante',)
