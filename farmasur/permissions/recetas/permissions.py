"""
Permisos para la app recetas.
Control de acceso basado en roles.
"""
from rest_framework import permissions
from usuarios.models import Usuario


class PuedeVerRecetas(permissions.BasePermission):
    """Acceso: Admin, Farmacéutico, Técnico."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.rol in [
            Usuario.Rol.ADMIN,
            Usuario.Rol.FARMACEUTICO,
            Usuario.Rol.TECNICO,
        ]


class SoloFarmaceutico(permissions.BasePermission):
    """Acceso restringido a farmacéuticos."""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.rol == Usuario.Rol.FARMACEUTICO


class PuedeModificarRecetas(permissions.BasePermission):
    """Modific: Admin, Farmacéutico."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return PuedeVerRecetas().has_permission(request, view)
        
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.rol in [
            Usuario.Rol.ADMIN,
            Usuario.Rol.FARMACEUTICO,
        ]


def puede_ver_recetas(usuario):
    """Helper: verifica si puede ver recetas."""
    if not usuario or not usuario.is_authenticated:
        return False
    return usuario.rol in [
        Usuario.Rol.ADMIN,
        Usuario.Rol.FARMACEUTICO,
        Usuario.Rol.TECNICO,
    ]


def puede_aprobar_receta(usuario):
    """Helper: verifica si puede aprobar recetas."""
    if not usuario or not usuario.is_authenticated:
        return False
    return usuario.rol == Usuario.Rol.FARMACEUTICO
