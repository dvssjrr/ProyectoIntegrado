"""
Permisos para la app ventas.
Control de acceso basado en roles.
"""
from rest_framework import permissions
from farmasur.models import Usuario


class PuedeVerVentas(permissions.BasePermission):
    """Acceso: Admin, Farmacéutico, Bodeguero."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.rol in [
            Usuario.Rol.ADMIN,
            Usuario.Rol.FARMACEUTICO,
            Usuario.Rol.BODEGUERO,
        ]


class PuedeModificarVentas(permissions.BasePermission):
    """Modific: Admin, Farmacéutico, Bodeguero."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return PuedeVerVentas().has_permission(request, view)
        
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.rol in [
            Usuario.Rol.ADMIN,
            Usuario.Rol.FARMACEUTICO,
            Usuario.Rol.BODEGUERO,
        ]


class PuedeGestionarCaja(permissions.BasePermission):
    """Gestión de caja: Admin, Farmacéutico."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.rol in [Usuario.Rol.ADMIN, Usuario.Rol.FARMACEUTICO]


def puede_ver_ventas(usuario):
    """Helper: verifica si puede ver ventas."""
    if not usuario or not usuario.is_authenticated:
        return False
    return usuario.rol in [
        Usuario.Rol.ADMIN,
        Usuario.Rol.FARMACEUTICO,
        Usuario.Rol.BODEGUERO,
    ]


def puede_crear_venta(usuario):
    """Helper: verifica si puede crear ventas."""
    if not usuario or not usuario.is_authenticated:
        return False
    return usuario.rol in [Usuario.Rol.ADMIN, Usuario.Rol.BODEGUERO]
