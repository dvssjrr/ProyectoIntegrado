"""
Permisos para la app inventario.
Control de acceso basado en roles.
"""
from rest_framework import permissions
from farmasur.models import Usuario


class PuedeVerInventario(permissions.BasePermission):
    """Acceso: Admin, Farmacéutico, Técnico."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.rol in [
            Usuario.Rol.ADMIN,
            Usuario.Rol.FARMACEUTICO,
            Usuario.Rol.TECNICO,
        ]


class PuedeModificarInventario(permissions.BasePermission):
    """Modific: Admin, Farmacéutico."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return PuedeVerInventario().has_permission(request, view)
        
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.rol in [
            Usuario.Rol.ADMIN,
            Usuario.Rol.FARMACEUTICO,
        ]


class SoloBodeguero(permissions.BasePermission):
    """Acceso restringido a bodegueros."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.rol == Usuario.Rol.BODEGUERO


def puede_ver_lotes(usuario):
    """Helper: verifica si puede ver lotes."""
    if not usuario or not usuario.is_authenticated:
        return False
    return usuario.rol in [Usuario.Rol.ADMIN, Usuario.Rol.FARMACEUTICO, Usuario.Rol.TECNICO]


def puede_modificar_lotes(usuario):
    """Helper: verifica si puede modificar lotes."""
    if not usuario or not usuario.is_authenticated:
        return False
    return usuario.rol in [Usuario.Rol.ADMIN, Usuario.Rol.FARMACEUTICO]
