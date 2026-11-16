from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from farmasur.models.inventario.models import Laboratorio, Lote, Merma, Producto
from farmasur.models.recetas.models import Receta, UnidosisAsistencial
from farmasur.models.usuarios.models import Usuario
from farmasur.models.ventas.models import CajaDiaria, ConvenioIsapre, POS

LABORATORIOS = ['Laboratorio Chile', 'Recalcine', 'Saval']

# sku, nombre, principio activo, presentacion, categoria, condicion, precio, stock minimo
PRODUCTOS = [
    ('7800000000011', 'Paracetamol 500mg', 'Paracetamol', 'Caja 16 comprimidos', Producto.Categoria.OTRO, Producto.CondicionVenta.LIBRE, 1990, 10),
    ('7800000000028', 'Ibuprofeno 400mg', 'Ibuprofeno', 'Caja 20 comprimidos', Producto.Categoria.ANTIINFLAMATORIO, Producto.CondicionVenta.LIBRE, 2990, 10),
    ('7800000000035', 'Vitamina C 1g', 'Acido ascorbico', 'Tubo 10 efervescentes', Producto.Categoria.VITAMINA, Producto.CondicionVenta.LIBRE, 3490, 8),
    ('7800000000042', 'Amoxicilina 500mg', 'Amoxicilina', 'Caja 21 capsulas', Producto.Categoria.OTRO, Producto.CondicionVenta.RECETA_SIMPLE, 5990, 10),
    ('7800000000059', 'Losartan 50mg', 'Losartan', 'Caja 30 comprimidos', Producto.Categoria.OTRO, Producto.CondicionVenta.RECETA_SIMPLE, 4490, 10),
]


class Command(BaseCommand):
    help = 'Carga datos de ejemplo de la farmacia (idempotente).'

    @transaction.atomic
    def handle(self, *args, **options):
        hoy = timezone.localdate()
        admin = Usuario.objects.filter(rol=Usuario.Rol.ADMIN).first()
        if admin is None:
            self.stderr.write('Crea primero un usuario ADMIN (createsuperuser).')
            return

        labs = [Laboratorio.objects.get_or_create(nombre=n)[0] for n in LABORATORIOS]

        productos = []
        for i, (sku, nombre, activo, pres, cat, cond, precio, minimo) in enumerate(PRODUCTOS):
            p, _ = Producto.objects.get_or_create(sku_codigo_barra=sku, defaults=dict(
                nombre_comercial=nombre, principio_activo=activo, presentacion=pres,
                categoria=cat, condicion_venta=cond, precio_clp=precio,
                stock_minimo_vitrina=minimo, laboratorio=labs[i % len(labs)]))
            productos.append(p)

        # (dias para vencer, vitrina, bodega): uno por vencer y uno con stock bajo
        plantillas = [(400, 40, 120), (60, 5, 30), (200, 25, 60)]
        lotes = []
        for p in productos:
            for n, (dias, vit, bod) in enumerate(plantillas, start=1):
                lote, _ = Lote.objects.get_or_create(
                    producto=p, codigo_lote=f'L{p.pk:03d}-{n}',
                    defaults=dict(fecha_vencimiento=hoy + timedelta(days=dias),
                                  stock_vitrina=vit, stock_bodega=bod,
                                  costo_compra=int(p.precio_clp * 0.6)))
                lotes.append(lote)

        if not Merma.objects.exists():
            Merma.objects.create(lote=lotes[1], cantidad=2, razon=Merma.Razon.VENCIMIENTO,
                                 descripcion='Envases danados en bodega')

        Receta.objects.get_or_create(folio='R-0001', defaults=dict(
            rut_paciente='12345678-5', nombre_paciente='Maria Gonzalez',
            rut_medico='11111111-1', nombre_medico='Dr. Pedro Soto', fecha_emision=hoy,
            medicamentos=[{'sku': productos[3].sku_codigo_barra, 'cantidad': 1, 'instrucciones': 'Cada 8 horas por 7 dias'}]))
        UnidosisAsistencial.objects.get_or_create(folio='U-0001', defaults=dict(
            numero_serie_carnet_paciente='A123456', rut_paciente='12345678-5',
            nombre_paciente='Maria Gonzalez', solicitado_por=admin,
            medicamentos=[{'sku': productos[0].sku_codigo_barra, 'cantidad': 2}]))

        ConvenioIsapre.objects.get_or_create(nombre='Consalud', defaults=dict(porcentaje_descuento=15))

        caja, _ = CajaDiaria.objects.get_or_create(
            caja_id='CAJA-01', estado=CajaDiaria.Estado.ABIERTA,
            defaults=dict(turno='MAÑANA', operario=admin, monto_inicial=50000))
        p = productos[0]
        POS.objects.get_or_create(folio='V-0001', defaults=dict(
            caja=caja, operario=admin, nombre_cliente='Cliente mostrador',
            subtotal=p.precio_clp * 2, total=p.precio_clp * 2,
            items=[{'sku': p.sku_codigo_barra, 'nombre': p.nombre_comercial, 'cantidad': 2,
                    'precio_unitario': p.precio_clp, 'subtotal': p.precio_clp * 2}]))

        self.stdout.write(self.style.SUCCESS('Datos de ejemplo cargados.'))
