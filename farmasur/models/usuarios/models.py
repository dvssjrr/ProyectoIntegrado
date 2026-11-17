from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import re

class UsuarioManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('rol', Usuario.Rol.ADMIN)
        return super().create_superuser(username, email, password, **extra_fields)


class Usuario(AbstractUser):
    """
    Modelo personalizado de Usuario con validación de RUT chileno (Módulo 11)
    y sistema de roles RBAC.
    """
    objects = UsuarioManager()
    REQUIRED_FIELDS = ['email', 'rut', 'nombre_completo']

    class Rol(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrador')
        FARMACEUTICO = 'FARMACEUTICO', _('Químico Farmacéutico')
        TECNICO = 'TECNICO', _('Técnico / Auxiliar de Farmacia')
        BODEGUERO = 'BODEGUERO', _('Bodeguero')

    rut = models.CharField(
        max_length=12, 
        unique=True, 
        db_index=True,
        help_text="Formato: XX.XXX.XXX-K (sin puntos ni guión en BD)"
    )
    nombre_completo = models.CharField(max_length=255)
    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.TECNICO
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'usuarios_usuario'
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['rut']),
            models.Index(fields=['rol']),
            models.Index(fields=['activo']),
        ]

    def __str__(self):
        return f"{self.nombre_completo} ({self.get_rol_display()})"

    @staticmethod
    def validar_rut(rut_input):
        """Valida un RUT chileno usando el dígito verificador (Módulo 11)."""
        rut_limpio = re.sub(r'[.\-]', '', str(rut_input)).upper()
        
        if not re.match(r'^\d{7,8}[0-9K]$', rut_limpio):
            return False, "Formato de RUT inválido"
        
        numeros = rut_limpio[:-1]
        digito_verificador = rut_limpio[-1]
        
        suma = sum(int(d) * (2 + i % 6) for i, d in enumerate(reversed(numeros)))
        digito_calculado = 11 - (suma % 11)
        
        if digito_calculado == 11:
            digito_calculado = '0'
        elif digito_calculado == 10:
            digito_calculado = 'K'
        else:
            digito_calculado = str(digito_calculado)
        
        if str(digito_verificador) != digito_calculado:
            return False, "Dígito verificador inválido"
        
        return True, rut_limpio

    def save(self, *args, **kwargs):
        """Valida el RUT antes de guardar."""
        if self.rut:
            valido, mensaje = self.validar_rut(self.rut)
            if not valido:
                raise ValueError(f"RUT inválido: {mensaje}")
            self.rut = re.sub(r'[.\-]', '', str(self.rut)).upper()
        super().save(*args, **kwargs)


class LogAuditoria(models.Model):
    """
    Registro inmutable de auditoría para cumplimiento de normativa ISP.
    Almacena eventos críticos del sistema con hash encadenado SHA-256.
    """
    class TipoEvento(models.TextChoices):
        LOGIN = 'LOGIN', _('Inicio de Sesión')
        LOGOUT = 'LOGOUT', _('Cierre de Sesión')
        VENTA = 'VENTA', _('Venta Registrada')
        RECETA_RETENIDA = 'RECETA_RETENIDA', _('Dispensación Receta Retenida')
        CAMBIO_INVENTARIO = 'CAMBIO_INVENTARIO', _('Cambio de Inventario')
        CAMBIO_USUARIO = 'CAMBIO_USUARIO', _('Modificación de Usuario')
        ACCESO_DENEGADO = 'ACCESO_DENEGADO', _('Acceso Denegado')
        EXPORT_DATOS = 'EXPORT_DATOS', _('Exportación de Datos')

    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    tipo_evento = models.CharField(max_length=30, choices=TipoEvento.choices)
    descripcion = models.TextField()
    datos_adicionales = models.JSONField(default=dict, blank=True)
    hash_sha256 = models.CharField(max_length=64, db_index=True)
    hash_anterior = models.CharField(max_length=64, blank=True)
    direccion_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'usuarios_log_auditoria'
        verbose_name = _('Log de Auditoría')
        verbose_name_plural = _('Logs de Auditoría')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['usuario', 'timestamp']),
            models.Index(fields=['tipo_evento', 'timestamp']),
        ]

    def __str__(self):
        return f"[{self.timestamp}] {self.get_tipo_evento_display()} - {self.usuario.username}"

    @classmethod
    def registrar(cls, usuario, tipo_evento, descripcion, datos_adicionales=None,
                  direccion_ip=None, user_agent=''):
        """Crea un registro encadenado por hash SHA-256 con el registro anterior."""
        import hashlib
        import json
        from django.utils import timezone

        datos = datos_adicionales or {}
        ultimo = cls.objects.order_by('-id').first()
        hash_anterior = ultimo.hash_sha256 if ultimo else ''
        contenido = '|'.join([
            hash_anterior, str(usuario.pk), str(tipo_evento), descripcion,
            json.dumps(datos, sort_keys=True, default=str), timezone.now().isoformat(),
        ])
        return cls.objects.create(
            usuario=usuario,
            tipo_evento=tipo_evento,
            descripcion=descripcion,
            datos_adicionales=datos,
            direccion_ip=direccion_ip,
            user_agent=user_agent,
            hash_anterior=hash_anterior,
            hash_sha256=hashlib.sha256(contenido.encode('utf-8')).hexdigest(),
        )
