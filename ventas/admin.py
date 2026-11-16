from django.contrib import admin
from .models import CajaDiaria, POS, ConvenioIsapre, Comprobante

@admin.register(CajaDiaria)
class CajaDiariaAdmin(admin.ModelAdmin):
    list_display = ('caja_id', 'fecha', 'turno', 'operario', 'estado', 'monto_inicial', 'total_ventas', 'diferencia')
    list_filter = ('estado', 'fecha', 'turno')
    search_fields = ('caja_id', 'operario__username')
    readonly_fields = ('fecha', 'hora_apertura', 'hora_cierre', 'total_ventas', 'total_descuentos')
    ordering = ('-fecha',)

@admin.register(POS)
class POSAdmin(admin.ModelAdmin):
    list_display = ('folio', 'fecha_venta', 'operario', 'rut_cliente', 'tipo_comprobante', 'total')
    list_filter = ('tipo_comprobante', 'fecha_venta', 'operario', 'requiere_receta_retenida')
    search_fields = ('folio', 'rut_cliente', 'nombre_cliente')
    readonly_fields = ('fecha_venta', 'folio')
    ordering = ('-fecha_venta',)
    
    fieldsets = (
        ('Folio y Fecha', {'fields': ('folio', 'fecha_venta', 'caja')}),
        ('Operario', {'fields': ('operario',)}),
        ('Cliente', {'fields': ('rut_cliente', 'nombre_cliente')}),
        ('Comprobante', {'fields': ('tipo_comprobante', 'comprobante_impreso')}),
        ('Montos', {'fields': ('subtotal', 'descuento_total', 'total')}),
        ('Convenio', {'fields': ('convenio_aplicado', 'porcentaje_descuento_convenio')}),
        ('Receta y Unidosis', {'fields': ('requiere_receta_retenida', 'receta_retenida', 'requiere_unidosis')}),
        ('Items', {'fields': ('items',)}),
        ('Adicional', {'fields': ('notas',)}),
    )

@admin.register(ConvenioIsapre)
class ConvenioIsapreAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'porcentaje_descuento', 'monto_maximo_descuento', 'requiere_autorizacion_qf', 'activo')
    list_filter = ('activo', 'requiere_autorizacion_qf', 'fecha_creacion')
    search_fields = ('nombre',)
    readonly_fields = ('fecha_creacion', 'fecha_ultima_modificacion')
    ordering = ('nombre',)

@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ('folio_comprobante', 'tipo', 'fecha_emision', 'nombre_receptor', 'total', 'estado')
    list_filter = ('tipo', 'estado', 'fecha_emision')
    search_fields = ('folio_comprobante', 'rut_receptor', 'nombre_receptor')
    readonly_fields = ('fecha_emision', 'fecha_vencimiento')
    ordering = ('-fecha_emision',)

