from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
from usuarios.models import Usuario, LogAuditoria
from inventario.models import Laboratorio, Producto, Lote, RecepcionProveedor
from recetas.models import Receta
from ventas.models import ConvenioIsapre, CajaDiaria


class Command(BaseCommand):
    help = 'Carga datos de prueba para el sistema Farmasur'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando seed de datos Farmasur...'))

        # 1. Crear usuarios de prueba
        self.crear_usuarios()

        # 2. Crear laboratorios
        self.crear_laboratorios()

        # 3. Crear medicamentos
        self.crear_medicamentos()

        # 4. Crear convenios Isapre
        self.crear_convenios()

        # 5. Crear cajas diarias de demostración
        self.crear_cajas_demo()

        self.stdout.write(self.style.SUCCESS('\n✓ Seed de datos completado exitosamente!'))
        self.stdout.write(self.style.WARNING('\nUsuarios de prueba creados:'))
        self.stdout.write('  - username: admin_user | rol: ADMIN | contraseña: Farmacia2026!')
        self.stdout.write('  - username: qf_maria | rol: FARMACEUTICO | contraseña: Farmacia2026!')
        self.stdout.write('  - username: aux_camila | rol: TECNICO | contraseña: Farmacia2026!')
        self.stdout.write('  - username: bod_carlos | rol: BODEGUERO | contraseña: Farmacia2026!')

    def crear_usuarios(self):
        self.stdout.write('Creando usuarios...')
        
        usuarios_data = [
            {
                'username': 'admin_user',
                'email': 'admin@farmasur.cl',
                'nombre_completo': 'Administrador Sistema',
                'rut': '123456789',
                'rol': Usuario.Rol.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'qf_maria',
                'email': 'maria@farmasur.cl',
                'nombre_completo': 'María González - Q.F.',
                'rut': '187654321',
                'rol': Usuario.Rol.FARMACEUTICO,
                'is_staff': True,
            },
            {
                'username': 'aux_camila',
                'email': 'camila@farmasur.cl',
                'nombre_completo': 'Camila Rodríguez - Auxiliar',
                'rut': '176543210',
                'rol': Usuario.Rol.TECNICO,
            },
            {
                'username': 'bod_carlos',
                'email': 'carlos@farmasur.cl',
                'nombre_completo': 'Carlos López - Bodeguero',
                'rut': '165432109',
                'rol': Usuario.Rol.BODEGUERO,
            },
        ]
        
        for user_data in usuarios_data:
            password = 'Farmacia2026!'
            user, created = Usuario.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'nombre_completo': user_data['nombre_completo'],
                    'rut': user_data['rut'],
                    'rol': user_data['rol'],
                    'is_staff': user_data.get('is_staff', False),
                    'is_superuser': user_data.get('is_superuser', False),
                }
            )
            
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f'  ✓ Usuario creado: {user.username} ({user.nombre_completo})')
            else:
                self.stdout.write(f'  ⊘ Usuario ya existe: {user.username}')

    def crear_laboratorios(self):
        self.stdout.write('Creando laboratorios...')
        
        laboratorios_data = [
            {'nombre': 'Laboratorio Chile', 'pais': 'Chile', 'email': 'info@labchile.cl'},
            {'nombre': 'Bagó', 'pais': 'Argentina', 'email': 'info@bago.ar'},
            {'nombre': 'Saval', 'pais': 'Chile', 'email': 'info@saval.cl'},
            {'nombre': 'Mintlab', 'pais': 'Chile', 'email': 'info@mintlab.cl'},
            {'nombre': 'Bayer', 'pais': 'Alemania', 'email': 'info@bayer.com'},
            {'nombre': 'Pfizer', 'pais': 'Estados Unidos', 'email': 'info@pfizer.com'},
        ]
        
        for lab_data in laboratorios_data:
            lab, created = Laboratorio.objects.get_or_create(
                nombre=lab_data['nombre'],
                defaults={
                    'pais': lab_data['pais'],
                    'email': lab_data['email'],
                }
            )
            if created:
                self.stdout.write(f'  ✓ Laboratorio creado: {lab.nombre}')

    def crear_medicamentos(self):
        self.stdout.write('Creando medicamentos con lotes...')
        
        medicamentos_data = [
            {
                'sku_codigo_barra': '7804379000011',
                'nombre_comercial': 'Paracetamol 500mg',
                'principio_activo': 'Paracetamol',
                'presentacion': '500mg cápsula',
                'categoria': Producto.Categoria.ANALGÉSICO,
                'laboratorio': 'Laboratorio Chile',
                'condicion_venta': Producto.CondicionVenta.LIBRE,
                'precio_clp': 2500,
                'stock_minimo_vitrina': 20,
                'lotes': [
                    {'codigo_lote': 'LOT001', 'stock_vitrina': 50, 'stock_bodega': 100, 'dias_vencimiento': 180},
                    {'codigo_lote': 'LOT002', 'stock_vitrina': 20, 'stock_bodega': 80, 'dias_vencimiento': 10},  # FEFO crítico
                ]
            },
            {
                'sku_codigo_barra': '7804379000012',
                'nombre_comercial': 'Ibuprofeno 400mg',
                'principio_activo': 'Ibuprofeno',
                'presentacion': '400mg cápsula',
                'categoria': Producto.Categoria.ANTIINFLAMATORIO,
                'laboratorio': 'Bagó',
                'condicion_venta': Producto.CondicionVenta.LIBRE,
                'precio_clp': 3500,
                'stock_minimo_vitrina': 15,
                'lotes': [
                    {'codigo_lote': 'LOT101', 'stock_vitrina': 40, 'stock_bodega': 90, 'dias_vencimiento': 150},
                    {'codigo_lote': 'LOT102', 'stock_vitrina': 0, 'stock_bodega': 60, 'dias_vencimiento': 25},
                ]
            },
            {
                'sku_codigo_barra': '7804379000013',
                'nombre_comercial': 'Amoxicilina 500mg',
                'principio_activo': 'Amoxicilina',
                'presentacion': '500mg cápsula',
                'categoria': Producto.Categoria.ANTIBIÓTICO,
                'laboratorio': 'Saval',
                'condicion_venta': Producto.CondicionVenta.RECETA_SIMPLE,
                'precio_clp': 5000,
                'stock_minimo_vitrina': 10,
                'lotes': [
                    {'codigo_lote': 'LOT201', 'stock_vitrina': 30, 'stock_bodega': 70, 'dias_vencimiento': 200},
                ]
            },
            {
                'sku_codigo_barra': '7804379000014',
                'nombre_comercial': 'Clonazepam 0.5mg',
                'principio_activo': 'Clonazepam',
                'presentacion': '0.5mg comprimido',
                'categoria': Producto.Categoria.CONTROLADO,
                'laboratorio': 'Mintlab',
                'condicion_venta': Producto.CondicionVenta.RECETA_RETENIDA,
                'precio_clp': 4500,
                'stock_minimo_vitrina': 5,
                'lotes': [
                    {'codigo_lote': 'LOT301', 'stock_vitrina': 15, 'stock_bodega': 40, 'dias_vencimiento': 120},
                ]
            },
            {
                'sku_codigo_barra': '7804379000015',
                'nombre_comercial': 'Tramadol 50mg',
                'principio_activo': 'Tramadol',
                'presentacion': '50mg comprimido',
                'categoria': Producto.Categoria.CONTROLADO,
                'laboratorio': 'Bayer',
                'condicion_venta': Producto.CondicionVenta.RECETA_RETENIDA,
                'precio_clp': 6000,
                'stock_minimo_vitrina': 5,
                'lotes': [
                    {'codigo_lote': 'LOT401', 'stock_vitrina': 10, 'stock_bodega': 30, 'dias_vencimiento': 100},
                ]
            },
            {
                'sku_codigo_barra': '7804379000016',
                'nombre_comercial': 'Omeprazol 20mg',
                'principio_activo': 'Omeprazol',
                'presentacion': '20mg cápsula',
                'categoria': Producto.Categoria.OTRO,
                'laboratorio': 'Pfizer',
                'condicion_venta': Producto.CondicionVenta.RECETA_SIMPLE,
                'precio_clp': 4000,
                'stock_minimo_vitrina': 15,
                'lotes': [
                    {'codigo_lote': 'LOT501', 'stock_vitrina': 25, 'stock_bodega': 60, 'dias_vencimiento': 180},
                ]
            },
            {
                'sku_codigo_barra': '7804379000017',
                'nombre_comercial': 'Vitamina C 1000mg',
                'principio_activo': 'Ácido Ascórbico',
                'presentacion': '1000mg comprimido',
                'categoria': Producto.Categoria.VITAMINA,
                'laboratorio': 'Laboratorio Chile',
                'condicion_venta': Producto.CondicionVenta.LIBRE,
                'precio_clp': 2000,
                'stock_minimo_vitrina': 30,
                'lotes': [
                    {'codigo_lote': 'LOT601', 'stock_vitrina': 100, 'stock_bodega': 200, 'dias_vencimiento': 300},
                ]
            },
        ]
        
        for med_data in medicamentos_data:
            lab = Laboratorio.objects.get(nombre=med_data['laboratorio'])
            producto, created = Producto.objects.get_or_create(
                sku_codigo_barra=med_data['sku_codigo_barra'],
                defaults={
                    'nombre_comercial': med_data['nombre_comercial'],
                    'principio_activo': med_data['principio_activo'],
                    'presentacion': med_data['presentacion'],
                    'categoria': med_data['categoria'],
                    'laboratorio': lab,
                    'condicion_venta': med_data['condicion_venta'],
                    'precio_clp': med_data['precio_clp'],
                    'stock_minimo_vitrina': med_data['stock_minimo_vitrina'],
                }
            )
            
            if created:
                self.stdout.write(f'  ✓ Producto creado: {producto.nombre_comercial}')
            
            # Crear lotes
            for lote_data in med_data['lotes']:
                fecha_vencimiento = timezone.now().date() + timedelta(days=lote_data['dias_vencimiento'])
                lote, created = Lote.objects.get_or_create(
                    producto=producto,
                    codigo_lote=lote_data['codigo_lote'],
                    defaults={
                        'fecha_vencimiento': fecha_vencimiento,
                        'stock_vitrina': lote_data['stock_vitrina'],
                        'stock_bodega': lote_data['stock_bodega'],
                        'costo_compra': int(producto.precio_clp * 0.6),
                    }
                )
                if created:
                    self.stdout.write(f'    ✓ Lote creado: {lote.codigo_lote} (Vence: {fecha_vencimiento})')

    def crear_convenios(self):
        self.stdout.write('Creando convenios Isapre...')
        
        convenios_data = [
            {
                'nombre': 'Consalud',
                'porcentaje_descuento': 15,
                'descripcion': 'Convenio Consalud con 15% de descuento',
            },
            {
                'nombre': 'Colmena',
                'porcentaje_descuento': 20,
                'descripcion': 'Convenio Colmena con 20% de descuento',
            },
            {
                'nombre': 'Banmédica',
                'porcentaje_descuento': 18,
                'descripcion': 'Convenio Banmédica con 18% de descuento',
            },
            {
                'nombre': 'Fonasa Tramo B/C/D',
                'porcentaje_descuento': 10,
                'descripcion': 'Descuento Fonasa 10%',
            },
        ]
        
        for conv_data in convenios_data:
            conv, created = ConvenioIsapre.objects.get_or_create(
                nombre=conv_data['nombre'],
                defaults={
                    'porcentaje_descuento': conv_data['porcentaje_descuento'],
                    'descripcion': conv_data['descripcion'],
                    'activo': True,
                }
            )
            if created:
                self.stdout.write(f'  ✓ Convenio creado: {conv.nombre} ({conv.porcentaje_descuento}%)')

    def crear_cajas_demo(self):
        self.stdout.write('Creando cajas diarias de demostración...')
        
        admin_user = Usuario.objects.get(username='admin_user')
        aux_user = Usuario.objects.get(username='aux_camila')
        
        for i in range(3):
            fecha = timezone.now().date() - timedelta(days=i)
            for turno in ['MAÑANA', 'TARDE']:
                caja, created = CajaDiaria.objects.get_or_create(
                    caja_id='CAJA-001',
                    fecha=fecha,
                    turno=turno,
                    defaults={
                        'operario': aux_user,
                        'monto_inicial': 500000,
                        'estado': CajaDiaria.Estado.CERRADA if i > 0 else CajaDiaria.Estado.ABIERTA,
                        'total_ventas': 150000 if i > 0 else 0,
                        'monto_cierre': 650000 if i > 0 else None,
                    }
                )
                if created:
                    self.stdout.write(f'  ✓ Caja creada: {caja.caja_id} - {fecha} ({turno})')
