from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from datetime import timedelta

class Laboratorio(models.Model):
    """Laboratorios proveedores de medicamentos."""
    nombre = models.CharField(max_length=255, unique=True, db_index=True)
    pais = models.CharField(max_length=100, default='Chile')
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    contacto = models.CharField(max_length=255, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventario_laboratorio'
        verbose_name = 'Laboratorio'
        verbose_name_plural = 'Laboratorios'
        ordering = ['nombre']
        indexes = [models.Index(fields=['nombre'])]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """
    Catálogo maestro de medicamentos con validación de condición de venta.
    """
    class CondicionVenta(models.TextChoices):
        LIBRE = 'LIBRE', 'Venta Libre'
        RECETA_SIMPLE = 'RECETA_SIMPLE', 'Receta Simple'
        RECETA_RETENIDA = 'RECETA_RETENIDA', 'Receta Retenida (Controlado)'

    class Categoria(models.TextChoices):
        ANALGÉSICO = 'ANALGESICO', 'Analgésico'
        ANTIINFLAMATORIO = 'ANTIINFLAMATORIO', 'Antiinflamatorio'
        ANTIBIÓTICO = 'ANTIBIOTICO', 'Antibiótico'
        ANTIHISTAMÍNICO = 'ANTIHISTAMINICO', 'Antihistamínico'
        VITAMINA = 'VITAMINA', 'Vitamina'
        CONTROLADO = 'CONTROLADO', 'Medicamento Controlado'
        OTRO = 'OTRO', 'Otro'

    sku_codigo_barra = models.CharField(
        max_length=50, 
        unique=True, 
        db_index=True,
        help_text="Código de barras o SKU único"
    )
    nombre_comercial = models.CharField(max_length=255, db_index=True)
    principio_activo = models.CharField(max_length=255)
    presentacion = models.CharField(max_length=100, help_text="Ej: 500mg cápsula")
    categoria = models.CharField(max_length=20, choices=Categoria.choices)
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.CASCADE, related_name='productos')
    condicion_venta = models.CharField(max_length=20, choices=CondicionVenta.choices)
    precio_clp = models.IntegerField(validators=[MinValueValidator(0)], help_text="Precio en CLP sin decimales")
    stock_minimo_vitrina = models.IntegerField(default=10, validators=[MinValueValidator(1)])
    requiere_cadena_frio = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventario_producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre_comercial']
        indexes = [
            models.Index(fields=['sku_codigo_barra']),
            models.Index(fields=['nombre_comercial']),
            models.Index(fields=['condicion_venta']),
        ]

    def __str__(self):
        return f"{self.nombre_comercial} ({self.presentacion})"

    @property
    def stock_total_vitrina(self):
        """Suma el stock de vitrina de todos los lotes activos."""
        return sum(lote.stock_vitrina for lote in self.lotes.filter(bloqueado_vencimiento=False, activo=True))

    @property
    def stock_total_bodega(self):
        """Suma el stock de bodega de todos los lotes activos."""
        return sum(lote.stock_bodega for lote in self.lotes.filter(bloqueado_vencimiento=False, activo=True))


class Lote(models.Model):
    """
    Gestión de lotes con algoritmo FEFO (First Expire First Out).
    """
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='lotes')
    codigo_lote = models.CharField(max_length=100, db_index=True)
    fecha_vencimiento = models.DateField()
    stock_vitrina = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    stock_bodega = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    costo_compra = models.IntegerField(validators=[MinValueValidator(0)], help_text="Costo en CLP")
    bloqueado_vencimiento = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventario_lote'
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        unique_together = ['producto', 'codigo_lote']
        ordering = ['fecha_vencimiento']
        indexes = [
            models.Index(fields=['producto', 'fecha_vencimiento']),
            models.Index(fields=['fecha_vencimiento']),
            models.Index(fields=['bloqueado_vencimiento']),
        ]

    def __str__(self):
        return f"{self.producto.nombre_comercial} - Lote {self.codigo_lote} (Venc: {self.fecha_vencimiento})"

    @property
    def dias_para_vencer(self):
        """Calcula días restantes hasta vencimiento."""
        hoy = timezone.now().date()
        return (self.fecha_vencimiento - hoy).days

    @property
    def estado_fefo(self):
        """Retorna el estado FEFO del lote."""
        dias = self.dias_para_vencer
        if dias < 0 or self.bloqueado_vencimiento:
            return 'VENCIDO'
        elif dias < 15:
            return 'CRÍTICO'
        elif dias < 30:
            return 'PRÓXIMO'
        else:
            return 'NORMAL'

    def bloquear_si_vencido(self):
        """Bloquea automáticamente si está vencido."""
        if self.dias_para_vencer < 0:
            self.bloqueado_vencimiento = True
            self.save()


class RecepcionProveedor(models.Model):
    """
    Recepción de cubetas de proveedores (Orden vs Factura).
    """
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente de Validación'
        VALIDADA = 'VALIDADA', 'Validada'
        RECHAZADA = 'RECHAZADA', 'Rechazada'

    numero_orden_compra = models.CharField(max_length=50, unique=True)
    numero_factura_proveedor = models.CharField(max_length=50, unique=True)
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    fecha_recepcion = models.DateTimeField(auto_now_add=True)
    datos_cubeta = models.JSONField(default=list, help_text="Array de {sku, cantidad, lote, vencimiento}")
    notas = models.TextField(blank=True)
    fecha_validacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'inventario_recepcion_proveedor'
        verbose_name = 'Recepción de Proveedor'
        verbose_name_plural = 'Recepciones de Proveedores'
        ordering = ['-fecha_recepcion']

    def __str__(self):
        return f"Recepción {self.numero_orden_compra} - {self.laboratorio.nombre}"


class Merma(models.Model):
    """
    Registro de medicamentos perdidos, dañados o vencidos.
    """
    class Razon(models.TextChoices):
        VENCIMIENTO = 'VENCIMIENTO', 'Vencimiento'
        DAÑO = 'DAÑO', 'Producto Dañado'
        PÉRDIDA = 'PERDIDA', 'Pérdida'
        AJUSTE_INVENTARIO = 'AJUSTE', 'Ajuste de Inventario'
        DEVOLUCIÓN_CLIENTE = 'DEVOLUCION', 'Devolución de Cliente'

    lote = models.ForeignKey(Lote, on_delete=models.PROTECT)
    cantidad = models.IntegerField(validators=[MinValueValidator(1)])
    razon = models.CharField(max_length=20, choices=Razon.choices)
    descripcion = models.TextField(blank=True)
    aprobado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='mermas_aprobadas'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'inventario_merma'
        verbose_name = 'Merma'
        verbose_name_plural = 'Mermas'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"Merma {self.lote.producto.nombre_comercial} ({self.cantidad}) - {self.get_razon_display()}"

