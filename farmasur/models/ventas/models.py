from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta

class CajaDiaria(models.Model):
    """
    Gestión de apertura y cierre de caja con validación de sesiones diarias.
    """
    class Estado(models.TextChoices):
        ABIERTA = 'ABIERTA', 'Abierta'
        CERRADA = 'CERRADA', 'Cerrada'
        SUSPENDIDA = 'SUSPENDIDA', 'Suspendida'

    caja_id = models.CharField(max_length=50, db_index=True)
    fecha = models.DateField(auto_now_add=True, db_index=True)
    turno = models.CharField(max_length=20, choices=[('MAÑANA', 'Mañana'), ('TARDE', 'Tarde'), ('NOCHE', 'Noche')])
    
    operario = models.ForeignKey('usuarios.Usuario', on_delete=models.PROTECT)
    
    monto_inicial = models.IntegerField(validators=[MinValueValidator(0)], help_text="Monto inicial en CLP")
    monto_cierre = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    diferencia = models.IntegerField(null=True, blank=True, help_text="Diferencia en CLP (Cierre - Inicial - Total Ventas)")
    
    total_ventas = models.IntegerField(default=0, validators=[MinValueValidator(0)], help_text="Total de ventas en CLP")
    total_descuentos = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ABIERTA)
    
    hora_apertura = models.DateTimeField(auto_now_add=True)
    hora_cierre = models.DateTimeField(null=True, blank=True)
    
    notas = models.TextField(blank=True)
    datos_cierre = models.JSONField(default=dict, blank=True, help_text="Resumen detallado del cierre")

    class Meta:
        db_table = 'ventas_caja_diaria'
        verbose_name = 'Caja Diaria'
        verbose_name_plural = 'Cajas Diarias'
        ordering = ['-fecha', '-hora_apertura']
        unique_together = ['caja_id', 'fecha', 'turno']
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f"Caja {self.caja_id} - {self.fecha} ({self.turno})"

    def cerrar_caja(self, monto_cierre):
        """Cierra la caja y calcula la diferencia."""
        if self.estado == self.Estado.ABIERTA:
            self.monto_cierre = monto_cierre
            self.diferencia = monto_cierre - self.monto_inicial - self.total_ventas
            self.estado = self.Estado.CERRADA
            self.hora_cierre = timezone.now()
            self.save()


class POS(models.Model):
    """
    Punto de Venta (Caja y Venta) con integración con CajaDiaria y Lotes (FEFO).
    """
    class TipoComprobante(models.TextChoices):
        BOLETA = 'BOLETA', 'Boleta'
        FACTURA = 'FACTURA', 'Factura'
        VOUCHER = 'VOUCHER', 'Voucher'

    caja = models.ForeignKey(CajaDiaria, on_delete=models.PROTECT, related_name='ventas')
    
    folio = models.CharField(max_length=50, unique=True, db_index=True)
    fecha_venta = models.DateTimeField(auto_now_add=True, db_index=True)
    
    operario = models.ForeignKey('usuarios.Usuario', on_delete=models.PROTECT)
    
    rut_cliente = models.CharField(max_length=12, blank=True, db_index=True)
    nombre_cliente = models.CharField(max_length=255, blank=True)
    
    tipo_comprobante = models.CharField(max_length=20, choices=TipoComprobante.choices, default=TipoComprobante.BOLETA)
    
    # Desglose de montos
    subtotal = models.IntegerField(validators=[MinValueValidator(0)])
    descuento_total = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total = models.IntegerField(validators=[MinValueValidator(0)])
    
    # Simulador Isapre/Seguros
    convenio_aplicado = models.CharField(max_length=100, blank=True, help_text="Nombre del convenio (Consalud, Colmena, etc.)")
    porcentaje_descuento_convenio = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Datos de receta retenida si aplica
    requiere_receta_retenida = models.BooleanField(default=False)
    receta_retenida = models.ForeignKey(
        'recetas.RecetaRetenidaISP',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Unidosis
    requiere_unidosis = models.BooleanField(default=False)
    
    # Items de venta
    items = models.JSONField(
        default=list,
        help_text="Array de {sku, nombre, cantidad, precio_unitario, lote_id, subtotal}"
    )
    
    # Metadata
    notas = models.TextField(blank=True)
    comprobante_impreso = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'ventas_pos'
        verbose_name = 'Venta POS'
        verbose_name_plural = 'Ventas POS'
        ordering = ['-fecha_venta']
        indexes = [
            models.Index(fields=['folio']),
            models.Index(fields=['fecha_venta']),
            models.Index(fields=['rut_cliente']),
        ]

    def __str__(self):
        return f"POS {self.folio} - {self.total} CLP"


class ConvenioIsapre(models.Model):
    """
    Simulador de convenios Isapre/Seguros con descuentos variables.
    """
    nombre = models.CharField(max_length=255, unique=True, db_index=True)
    descripcion = models.TextField(blank=True)
    porcentaje_descuento = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Porcentaje de descuento (0-100%)"
    )
    
    # Restricciones
    medicamentos_excluidos = models.JSONField(
        default=list,
        blank=True,
        help_text="Array de SKUs excluidos del descuento"
    )
    
    monto_maximo_descuento = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Monto máximo de descuento por transacción (None = sin límite)"
    )
    
    requiere_autorizacion_qf = models.BooleanField(
        default=False,
        help_text="Requiere aprobación de Químico Farmacéutico"
    )
    
    activo = models.BooleanField(default=True, db_index=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ventas_convenio_isapre'
        verbose_name = 'Convenio Isapre'
        verbose_name_plural = 'Convenios Isapre'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.porcentaje_descuento}%)"


class Comprobante(models.Model):
    """
    Emisión de Boleta/Factura electrónica simulada con generación imprimible.
    """
    class TipoComprobante(models.TextChoices):
        BOLETA = 'BOLETA', 'Boleta'
        FACTURA = 'FACTURA', 'Factura'

    venta_pos = models.OneToOneField(POS, on_delete=models.CASCADE, related_name='comprobante')
    
    tipo = models.CharField(max_length=20, choices=TipoComprobante.choices)
    folio_comprobante = models.CharField(max_length=50, unique=True, db_index=True)
    
    rut_receptor = models.CharField(max_length=12, blank=True)
    nombre_receptor = models.CharField(max_length=255)
    giro_receptor = models.CharField(max_length=255, blank=True)
    direccion_receptor = models.CharField(max_length=255, blank=True)
    
    fecha_emision = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    
    neto = models.IntegerField(validators=[MinValueValidator(0)])
    iva = models.IntegerField(validators=[MinValueValidator(0)])
    total = models.IntegerField(validators=[MinValueValidator(0)])
    
    # Datos del emisor (Farmasur)
    rut_emisor = models.CharField(max_length=12, default='76123456-7')
    nombre_emisor = models.CharField(max_length=255, default='Farmasur')
    
    # Archivo generado
    archivo_pdf = models.FileField(upload_to='comprobantes/%Y/%m/%d/', null=True, blank=True)
    
    # Metadata
    estado = models.CharField(
        max_length=20,
        choices=[('EMITIDA', 'Emitida'), ('ANULADA', 'Anulada')],
        default='EMITIDA'
    )
    notas = models.TextField(blank=True)

    class Meta:
        db_table = 'ventas_comprobante'
        verbose_name = 'Comprobante'
        verbose_name_plural = 'Comprobantes'
        ordering = ['-fecha_emision']

    def __str__(self):
        return f"{self.get_tipo_display()} {self.folio_comprobante}"

