from django.contrib import admin
from .models import Receta, RecetaRetenidaISP, UnidosisAsistencial

@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ('folio', 'nombre_paciente', 'rut_paciente', 'nombre_medico', 'estado', 'fecha_emision', 'dias_desde_emision')
    list_filter = ('estado', 'fecha_emision', 'fecha_registro')
    search_fields = ('folio', 'rut_paciente', 'nombre_paciente', 'rut_medico', 'nombre_medico')
    readonly_fields = ('fecha_registro', 'fecha_aprobacion', 'fecha_dispensacion', 'dias_desde_emision', 'esta_vigente')
    ordering = ('-fecha_registro',)
    
    fieldsets = (
        ('Folio y Fecha', {'fields': ('folio', 'fecha_emision', 'fecha_registro')}),
        ('Paciente', {'fields': ('rut_paciente', 'nombre_paciente')}),
        ('Prescriptor', {'fields': ('rut_medico', 'nombre_medico', 'notas_prescriptor')}),
        ('Medicamentos', {'fields': ('medicamentos',)}),
        ('Validación', {'fields': ('estado', 'esta_vigente', 'dias_desde_emision', 'aprobado_por', 'fecha_aprobacion', 'razon_rechazo')}),
        ('Dispensación', {'fields': ('fecha_dispensacion',)}),
        ('Adicional', {'fields': ('datos_adicionales',)}),
    )

@admin.register(RecetaRetenidaISP)
class RecetaRetenidaISPAdmin(admin.ModelAdmin):
    list_display = ('folio_isp', 'receta', 'dispensado_por', 'fecha_dispensacion')
    list_filter = ('fecha_dispensacion', 'dispensado_por')
    search_fields = ('folio_isp', 'receta__folio', 'receta__nombre_paciente')
    readonly_fields = ('fecha_dispensacion', 'hash_sha256', 'hash_anterior')
    ordering = ('-fecha_dispensacion',)

@admin.register(UnidosisAsistencial)
class UnidosisAsistencialAdmin(admin.ModelAdmin):
    list_display = ('folio', 'nombre_paciente', 'rut_paciente', 'estado', 'fecha_solicitud', 'fecha_dispensacion')
    list_filter = ('estado', 'fecha_solicitud')
    search_fields = ('folio', 'rut_paciente', 'nombre_paciente')
    readonly_fields = ('fecha_solicitud', 'fecha_dispensacion')
    ordering = ('-fecha_solicitud',)

