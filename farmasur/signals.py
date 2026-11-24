from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from farmasur.models.usuarios.models import LogAuditoria


def _registrar_sesion(sender, request, user, evento, descripcion):
    if user is None:
        return
    LogAuditoria.registrar(
        usuario=user,
        tipo_evento=evento,
        descripcion=descripcion,
        datos_adicionales={
            'nombre_completo': user.nombre_completo,
            'rut': user.rut,
            'email': user.email,
        },
        direccion_ip=request.META.get('REMOTE_ADDR') if request else None,
        user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
    )


@receiver(user_logged_in)
def registrar_inicio_sesion(sender, request, user, **kwargs):
    _registrar_sesion(
        sender, request, user, LogAuditoria.TipoEvento.LOGIN, 'Inicio de sesión'
    )


@receiver(user_logged_out)
def registrar_cierre_sesion(sender, request, user, **kwargs):
    _registrar_sesion(
        sender, request, user, LogAuditoria.TipoEvento.LOGOUT, 'Cierre de sesión'
    )
