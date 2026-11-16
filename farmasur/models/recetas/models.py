from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from datetime import timedelta


class DetalleReceta(models.Model):
    """
    Detalles de medicamentos en una receta.
    """
    class Meta:
        db_table = 'recetas_detalle_receta'
        verbose_name = 'Detalle de Receta'
        verbose_name_plural = 'Detalles de Receta'
    
    def __str__(self):
        return f"Detalle Receta"


class Receta(models.Model):
    """
    Validación clínica y legal de recetas médicas con bloqueo automático a 30 días.
    """
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente de Validación'
        APROBADA = 'APROBADA', 'Aprobada'
        RECHAZADA = 'RECHAZADA', 'Rechazada'
        DISPENSADA = 'DISPENSADA', 'Dispensada'
        VENCIDA = 'VENCIDA', 'Vencida (> 30 días)'

    folio = models.CharField(max_length=50, unique=True, db_index=True)
    rut_paciente = models.CharField(max_length=12)
    nombre_paciente = models.CharField(max_length=255)
    rut_medico = models.CharField(max_length=12)
    nombre_medico = models.CharField(max_length=255)
    fecha_emision = models.DateField()
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    medicamentos = models.JSONField(default=list, help_text="Array de {sku, cantidad, instrucciones}")
    notas_prescriptor = models.TextField(blank=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    aprobado_por = models.ForeignKey(
        'farmasur.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recetas_aprobadas'
    )
    fecha_dispensacion = models.DateTimeField(null=True, blank=True)
    razon_rechazo = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    datos_adicionales = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'recetas_receta'
        verbose_name = 'Receta'
        verbose_name_plural = 'Recetas'
        ordering = ['-fecha_registro']
        indexes = [
            models.Index(fields=['folio']),
            models.Index(fields=['rut_paciente']),
            models.Index(fields=['estado', 'fecha_emision']),
        ]

    def __str__(self):
        return f"Receta {self.folio} - {self.nombre_paciente}"

    @property
    def dias_desde_emision(self):
        """Calcula días desde emisión de la receta."""
        return (timezone.now().date() - self.fecha_emision).days

    @property
    def esta_vigente(self):
        """Verifica si la receta está vigente (< 30 días)."""
        return self.dias_desde_emision < 30

    def validar_vigencia_automatica(self):
        """Bloquea automáticamente recetas vencidas (> 30 días)."""
        if not self.esta_vigente and self.estado != self.Estado.VENCIDA:
            self.estado = self.Estado.VENCIDA
            self.save()


class RecetaRetenidaISP(models.Model):
    """
    Libro Digital ISP de Medicamentos Controlados con registro inmutable
    y almacenamiento JSONB para datos estructurados.
    """
    receta = models.OneToOneField(Receta, on_delete=models.PROTECT, related_name='receta_retenida')
    numero_serie_carnet_paciente = models.CharField(max_length=20)
    numero_serie_carnet_medico = models.CharField(max_length=20)
    
    # Almacenamiento JSONB con datos inmutables
    datos_receta_jsonb = models.JSONField(
        help_text="Datos estructurados inmutables de la receta retenida"
    )
    
    # Metadata del registro ISP
    folio_isp = models.CharField(max_length=50, unique=True, db_index=True)
    fecha_dispensacion = models.DateTimeField(auto_now_add=True)
    dispensado_por = models.ForeignKey(
        'farmasur.Usuario',
        on_delete=models.PROTECT,
        related_name='recetas_retenidas_dispensadas'
    )
    
    # Hash encadenado para integridad
    hash_sha256 = models.CharField(max_length=64, db_index=True)
    hash_anterior = models.CharField(max_length=64, blank=True)
    
    class Meta:
        db_table = 'recetas_receta_retenida_isp'
        verbose_name = 'Receta Retenida ISP'
        verbose_name_plural = 'Recetas Retenidas ISP'
        ordering = ['-fecha_dispensacion']
        indexes = [
            models.Index(fields=['folio_isp']),
            models.Index(fields=['fecha_dispensacion']),
        ]

    def __str__(self):
        return f"Receta Retenida ISP {self.folio_isp} - {self.receta.nombre_paciente}"


class UnidosisAsistencial(models.Model):
    """
    Extracción de medicamentos en unidosis para ambiente asistencial.
    Requiere validación de Carnet de Identidad.
    """
    class Estado(models.TextChoices):
        SOLICITADA = 'SOLICITADA', 'Solicitada'
        PREPARADA = 'PREPARADA', 'Preparada'
        DISPENSADA = 'DISPENSADA', 'Dispensada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    folio = models.CharField(max_length=50, unique=True, db_index=True)
    numero_serie_carnet_paciente = models.CharField(max_length=20)
    rut_paciente = models.CharField(max_length=12)
    nombre_paciente = models.CharField(max_length=255)
    
    medicamentos = models.JSONField(
        default=list,
        help_text="Array de {sku, cantidad, instrucciones_uso}"
    )
    
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.SOLICITADA)
    observaciones = models.TextField(blank=True)
    
    solicitado_por = models.ForeignKey(
        'farmasur.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='unidosis_solicitadas'
    )
    
    dispensado_por = models.ForeignKey(
        'farmasur.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='unidosis_dispensadas'
    )
    
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_dispensacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'recetas_unidosis_asistencial'
        verbose_name = 'Unidosis Asistencial'
        verbose_name_plural = 'Unidosis Asistencial'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"Unidosis {self.folio} - {self.nombre_paciente}"

