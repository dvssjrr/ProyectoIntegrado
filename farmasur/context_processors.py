from farmasur.models.usuarios.models import Usuario


def acceso(request):
    """Permisos granulares en UI según matriz RBAC."""
    user = request.user
    if not user.is_authenticated:
        return {}
    rol = user.rol
    admin = rol == Usuario.Rol.ADMIN
    qf = rol == Usuario.Rol.FARMACEUTICO
    tecnico = rol == Usuario.Rol.TECNICO
    bodeguero = rol == Usuario.Rol.BODEGUERO
    return {'acceso': {
        'admin': admin,
        'qf': qf,
        'tecnico': tecnico,
        'bodeguero': bodeguero,
        'catalogo_editar': admin,
        'inventario_lotes_gestion': admin or bodeguero,
        'mermas': admin or qf,
        'solo_vitrina': tecnico,
        'libro': admin or qf or tecnico,
        'libro_autorizar': qf,
        'libro_registrar': qf or tecnico,
        'ventas': qf or tecnico,
        'config': admin,
    }}
