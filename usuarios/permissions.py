"""
Permisos para la app usuarios.
Control de acceso basado en roles (RBAC).
"""
from rest_framework import permissions
from .models import Usuario


class EsAdmin(permissions.BasePermission):
    """Solo permite acceso si el usuario es Administrador."""
    message = "Solo administradores pueden acceder a este recurso."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.rol == Usuario.Rol.ADMIN


class EsAdminOLectura(permissions.BasePermission):
    """Administradores: acceso completo. Otros: solo lectura."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.rol == Usuario.Rol.ADMIN


class EsUsuarioMismoOAdmin(permissions.BasePermission):
    """Los usuarios solo pueden ver/editar sus propios datos, administradores ven todo."""
    
    def has_object_permission(self, request, view, obj):
        if request.user.rol == Usuario.Rol.ADMIN:
            return True
        
        return obj == request.user


def es_admin(usuario):
    """Helper: verifica si un usuario es administrador."""
    return usuario and usuario.is_authenticated and usuario.rol == Usuario.Rol.ADMIN


def tiene_permiso_ver_usuarios(usuario):
    """Helper: verifica si un usuario puede ver el listado de usuarios."""
    if not usuario or not usuario.is_authenticated:
        return False
    
    # Admin y Farmacéutico pueden ver usuarios
    return usuario.rol in [Usuario.Rol.ADMIN, Usuario.Rol.FARMACEUTICO]
