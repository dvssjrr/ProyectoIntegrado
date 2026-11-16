from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, LogAuditoria

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('username', 'nombre_completo', 'rut', 'rol', 'activo', 'fecha_creacion')
    list_filter = ('rol', 'activo', 'fecha_creacion')
    search_fields = ('username', 'email', 'rut', 'nombre_completo')
    ordering = ('-fecha_creacion',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('nombre_completo', 'rut', 'email', 'first_name', 'last_name')}),
        ('Permisos', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Estado', {'fields': ('activo', 'fecha_creacion', 'fecha_ultima_modificacion')}),
    )

@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'usuario', 'tipo_evento', 'descripcion_corta')
    list_filter = ('tipo_evento', 'timestamp', 'usuario')
    search_fields = ('usuario__username', 'descripcion')
    readonly_fields = ('timestamp', 'hash_sha256', 'hash_anterior')
    ordering = ('-timestamp',)
    
    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'
    
    fieldsets = (
        ('Evento', {'fields': ('usuario', 'tipo_evento', 'descripcion', 'timestamp')}),
        ('Datos Adicionales', {'fields': ('datos_adicionales', 'hash_sha256', 'hash_anterior')}),
        ('Sesión', {'fields': ('direccion_ip', 'user_agent')}),
    )
