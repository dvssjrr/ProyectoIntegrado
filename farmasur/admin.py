"""
Administración centralizada de la aplicación Farmasur.
"""
from django.contrib import admin

# Importar modelos
from farmasur.models.usuarios.models import Usuario, LogAuditoria
from farmasur.models.inventario.models import (
    Medicamento,
    StockVitrina,
    StockBodega,
    MovimientoInventario,
    Lote,
)
from farmasur.models.recetas.models import Receta, DetalleReceta, LibroISP
from farmasur.models.ventas.models import Venta, DetalleVenta, Caja

# ============================================================================
# USUARIOS
# ============================================================================

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre', 'email', 'rol', 'activo', 'fecha_creacion')
    list_filter = ('rol', 'activo', 'fecha_creacion')
    search_fields = ('rut', 'nombre', 'email')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    fieldsets = (
        ('Información Personal', {
            'fields': ('rut', 'nombre', 'email', 'telefono')
        }),
        ('Credenciales', {
            'fields': ('contrasena',)
        }),
        ('Permisos', {
            'fields': ('rol', 'activo')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'accion', 'tabla', 'fecha')
    list_filter = ('accion', 'tabla', 'fecha')
    search_fields = ('usuario__nombre', 'accion', 'tabla')
    readonly_fields = ('hash_anterior', 'hash_actual')


# ============================================================================
# INVENTARIO
# ============================================================================

@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'principio_activo', 'presentacion', 'precio')
    list_filter = ('presentacion', 'precio')
    search_fields = ('codigo', 'nombre', 'principio_activo')


@admin.register(StockVitrina)
class StockVitrinaAdmin(admin.ModelAdmin):
    list_display = ('medicamento', 'cantidad', 'stock_minimo', 'fecha_actualizacion')
    list_filter = ('fecha_actualizacion',)
    search_fields = ('medicamento__nombre',)


@admin.register(StockBodega)
class StockBodegaAdmin(admin.ModelAdmin):
    list_display = ('medicamento', 'cantidad', 'fecha_actualizacion')
    list_filter = ('fecha_actualizacion',)
    search_fields = ('medicamento__nombre',)


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('medicamento', 'tipo_movimiento', 'cantidad', 'fecha')
    list_filter = ('tipo_movimiento', 'fecha')
    search_fields = ('medicamento__nombre',)


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('numero_lote', 'medicamento', 'cantidad_inicial', 'fecha_vencimiento')
    list_filter = ('fecha_vencimiento',)
    search_fields = ('numero_lote', 'medicamento__nombre')


# ============================================================================
# RECETAS
# ============================================================================

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'paciente', 'medico', 'fecha_emision', 'estado')
    list_filter = ('estado', 'fecha_emision')
    search_fields = ('numero', 'paciente', 'medico')


@admin.register(DetalleReceta)
class DetalleRecetaAdmin(admin.ModelAdmin):
    list_display = ('receta', 'medicamento', 'cantidad', 'dosis')
    list_filter = ('receta__fecha_emision',)
    search_fields = ('receta__numero', 'medicamento__nombre')


@admin.register(LibroISP)
class LibroISPAdmin(admin.ModelAdmin):
    list_display = ('numero_registro', 'receta', 'fecha_registro', 'estado')
    list_filter = ('estado', 'fecha_registro')
    search_fields = ('numero_registro', 'receta__numero')


# ============================================================================
# VENTAS
# ============================================================================

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cliente', 'fecha', 'total', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('numero', 'cliente')


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'medicamento', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('venta__fecha',)
    search_fields = ('venta__numero', 'medicamento__nombre')


@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'fecha', 'saldo_inicial', 'saldo_final', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('numero',)
