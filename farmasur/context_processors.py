from farmasur.models.usuarios.models import Usuario


def acceso(request):
    """Secciones del menú visibles según el rol (el administrador ve todo)."""
    user = request.user
    if not user.is_authenticated:
        return {}
    rol = user.rol
    admin = rol == Usuario.Rol.ADMIN
    return {'acceso': {
        'inventario_gestion': admin or rol in (Usuario.Rol.FARMACEUTICO, Usuario.Rol.BODEGUERO),
        'libro': admin or rol in (Usuario.Rol.FARMACEUTICO, Usuario.Rol.TECNICO),
        'ventas': admin or rol in (Usuario.Rol.FARMACEUTICO, Usuario.Rol.TECNICO),
        'config': admin,
    }}
