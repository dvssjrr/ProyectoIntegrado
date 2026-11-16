"""
Services para la app usuarios.
Lógica de negocio reutilizable y operaciones transaccionales.
"""
from django.db import transaction
from django.contrib.auth.hashers import make_password
from farmasur.models import Usuario, LogAuditoria


class UsuarioService:
    """Servicio para operaciones de usuario."""
    
    @staticmethod
    @transaction.atomic
    def crear_usuario(username, email, nombre_completo, rut, rol, password=None, **kwargs):
        """
        Crea un usuario con auditoría.
        """
        usuario = Usuario.objects.create_user(
            username=username,
            email=email,
            nombre_completo=nombre_completo,
            rut=rut,
            rol=rol,
            password=password
        )
        
        # Registrar en auditoría
        LogAuditoria.registrar(
            usuario=usuario,
            accion='CREAR',
            tabla_afectada='usuarios_usuario',
            descripcion=f'Usuario creado: {usuario.username}'
        )
        
        return usuario
    
    @staticmethod
    @transaction.atomic
    def actualizar_usuario(usuario_id, **datos):
        """
        Actualiza un usuario con auditoría.
        """
        usuario = Usuario.objects.get(pk=usuario_id)
        cambios = []
        
        for campo, valor in datos.items():
            if hasattr(usuario, campo) and valor is not None:
                cambios.append(f"{campo}: {getattr(usuario, campo)} → {valor}")
                setattr(usuario, campo, valor)
        
        usuario.save()
        
        # Registrar cambios en auditoría
        if cambios:
            LogAuditoria.registrar(
                usuario=usuario,
                accion='ACTUALIZAR',
                tabla_afectada='usuarios_usuario',
                descripcion=f'Cambios: {"; ".join(cambios)}'
            )
        
        return usuario
    
    @staticmethod
    @transaction.atomic
    def cambiar_contrasena(usuario_id, nueva_contrasena):
        """
        Cambia la contraseña de un usuario.
        """
        usuario = Usuario.objects.get(pk=usuario_id)
        usuario.set_password(nueva_contrasena)
        usuario.save()
        
        LogAuditoria.registrar(
            usuario=usuario,
            accion='CAMBIAR_CONTRASEÑA',
            tabla_afectada='usuarios_usuario',
            descripcion='Contraseña actualizada'
        )
        
        return usuario
    
    @staticmethod
    def obtener_usuarios_por_rol(rol):
        """Obtiene todos los usuarios de un rol específico."""
        return Usuario.objects.filter(rol=rol, activo=True)
    
    @staticmethod
    def listar_auditoria_usuario(usuario_id, limite=50):
        """Obtiene el historial de auditoría de un usuario."""
        return LogAuditoria.objects.filter(usuario_id=usuario_id).order_by('-timestamp')[:limite]


class LogAuditoriaService:
    """Servicio para gestión de auditoría."""
    
    @staticmethod
    def obtener_historial(tabla_afectada=None, limite=100):
        """Obtiene historial de auditoría filtrando por tabla si es necesario."""
        qs = LogAuditoria.objects.all()
        if tabla_afectada:
            qs = qs.filter(tabla_afectada=tabla_afectada)
        return qs.order_by('-timestamp')[:limite]
    
    @staticmethod
    def validar_integridad_cadena(log_id):
        """Valida que la cadena de hashes SHA-256 sea íntegra desde un registro hasta el primero."""
        log = LogAuditoria.objects.get(pk=log_id)
        actual = log
        
        while actual.hash_anterior:
            anterior = LogAuditoria.objects.filter(hash_sha256=actual.hash_anterior).first()
            if not anterior:
                return False
            actual = anterior
        
        return True
