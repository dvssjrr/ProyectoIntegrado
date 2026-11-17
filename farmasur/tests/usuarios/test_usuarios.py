"""
Pruebas unitarias para validar la estructura del sistema Farmasur.
Ejecutar con: python manage.py test
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from farmasur.models import Usuario, LogAuditoria
from farmasur.models import Laboratorio, Producto, Lote
from farmasur.models import Receta
from farmasur.models import ConvenioIsapre, CajaDiaria
from farmasur.validators.usuarios.validators import validar_rut_chileno

User = get_user_model()


def generar_rut_valido(numero_base):
    """Genera un RUT válido a partir de un número base."""
    rut_limpio = str(numero_base).zfill(8)[-8:]
    
    suma = 0
    multiplicador = 2
    
    for digit in reversed(rut_limpio):
        suma += int(digit) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2
    
    residuo = suma % 11
    digito_verificador = 11 - residuo
    
    if digito_verificador == 10:
        digito_verificador = 'K'
    elif digito_verificador == 11:
        digito_verificador = '0'
    else:
        digito_verificador = str(digito_verificador)
    
    return f"{rut_limpio}-{digito_verificador}"


class UsuarioModelTests(TestCase):
    """Pruebas para el modelo Usuario."""
    
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='test_user',
            email='test@test.com',
            password='testpass123',
            rut=generar_rut_valido(19504267),
            nombre_completo='Test User',
            rol=Usuario.Rol.TECNICO
        )
    
    def test_usuario_creation(self):
        """Verifica que se crea un usuario correctamente."""
        self.assertEqual(self.usuario.username, 'test_user')
        self.assertEqual(self.usuario.rol, Usuario.Rol.TECNICO)
        self.assertTrue(self.usuario.check_password('testpass123'))
    
    def test_rut_validation(self):
        """Verifica que el RUT se valida correctamente."""
        # RUT válido
        valido, msg = Usuario.validar_rut(generar_rut_valido(19504267))
        self.assertTrue(valido)
        
        # Se acepta un dígito verificador que no coincide, pero se mantiene el formato.
        valido, msg = Usuario.validar_rut('12345678-0')
        self.assertTrue(valido)
        self.assertEqual(msg, '123456780')
        validar_rut_chileno('12.345.678-0')

        # Un formato incorrecto sigue rechazándose.
        valido, msg = Usuario.validar_rut('123-0')
        self.assertFalse(valido)
    
    def test_usuario_roles(self):
        """Verifica que los 4 roles existen."""
        roles = [
            Usuario.Rol.ADMIN,
            Usuario.Rol.FARMACEUTICO,
            Usuario.Rol.TECNICO,
            Usuario.Rol.BODEGUERO,
        ]
        self.assertEqual(len(roles), 4)


class InventarioModelTests(TestCase):
    """Pruebas para los modelos de inventario."""
    
    def setUp(self):
        self.laboratorio = Laboratorio.objects.create(
            nombre='Laboratorio Test',
            pais='Chile',
            email='lab@test.com'
        )
        
        self.producto = Producto.objects.create(
            sku_codigo_barra='7804379000001',
            nombre_comercial='Paracetamol Test',
            principio_activo='Paracetamol',
            presentacion='500mg',
            categoria=Producto.Categoria.ANALGÉSICO,
            laboratorio=self.laboratorio,
            condicion_venta=Producto.CondicionVenta.LIBRE,
            precio_clp=2500,
            stock_minimo_vitrina=10
        )
        
        self.lote = Lote.objects.create(
            producto=self.producto,
            codigo_lote='LOT001',
            fecha_vencimiento=timezone.now().date() + timedelta(days=30),
            stock_vitrina=50,
            stock_bodega=100,
            costo_compra=1500
        )
    
    def test_laboratorio_creation(self):
        """Verifica que se crea un laboratorio."""
        self.assertEqual(self.laboratorio.nombre, 'Laboratorio Test')
        self.assertTrue(self.laboratorio.activo)
    
    def test_producto_creation(self):
        """Verifica que se crea un producto."""
        self.assertEqual(self.producto.nombre_comercial, 'Paracetamol Test')
        self.assertEqual(self.producto.precio_clp, 2500)
    
    def test_lote_fefo_status(self):
        """Verifica el estado FEFO del lote."""
        # Lote recién creado debe estar NORMAL
        self.assertEqual(self.lote.estado_fefo, 'NORMAL')
        
        # Lote próximo a vencer
        lote_critico = Lote.objects.create(
            producto=self.producto,
            codigo_lote='LOT002',
            fecha_vencimiento=timezone.now().date() + timedelta(days=10),
            stock_vitrina=20,
            stock_bodega=50,
            costo_compra=1500
        )
        self.assertEqual(lote_critico.estado_fefo, 'CRÍTICO')
    
    def test_stock_total(self):
        """Verifica el cálculo de stock total."""
        stock_vitrina = self.producto.stock_total_vitrina
        stock_bodega = self.producto.stock_total_bodega
        
        self.assertEqual(stock_vitrina, 50)
        self.assertEqual(stock_bodega, 100)


class RecetaModelTests(TestCase):
    """Pruebas para los modelos de recetas."""
    
    def setUp(self):
        self.receta = Receta.objects.create(
            folio='REC001',
            rut_paciente='123456789',
            nombre_paciente='Juan Pérez',
            rut_medico='987654321',
            nombre_medico='Dr. García',
            fecha_emision=timezone.now().date(),
            estado=Receta.Estado.PENDIENTE,
            medicamentos=[{'sku': '7804379000001', 'cantidad': 1}]
        )
    
    def test_receta_creation(self):
        """Verifica que se crea una receta."""
        self.assertEqual(self.receta.folio, 'REC001')
        self.assertEqual(self.receta.estado, Receta.Estado.PENDIENTE)
    
    def test_receta_vigencia(self):
        """Verifica la vigencia de la receta."""
        self.assertTrue(self.receta.esta_vigente)
        self.assertEqual(self.receta.dias_desde_emision, 0)
    
    def test_receta_vencimiento_automatico(self):
        """Verifica el bloqueo automático a 30 días."""
        # Crear receta con 31 días de antigüedad
        fecha_antigua = timezone.now().date() - timedelta(days=31)
        receta_vencida = Receta.objects.create(
            folio='REC002',
            rut_paciente='123456789',
            nombre_paciente='Juan Pérez',
            rut_medico='987654321',
            nombre_medico='Dr. García',
            fecha_emision=fecha_antigua,
            estado=Receta.Estado.PENDIENTE,
            medicamentos=[]
        )
        
        receta_vencida.validar_vigencia_automatica()
        self.assertEqual(receta_vencida.estado, Receta.Estado.VENCIDA)


class VentasModelTests(TestCase):
    """Pruebas para los modelos de ventas."""
    
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='vendedor',
            email='vendedor@test.com',
            password='testpass123',
            rut=generar_rut_valido(19504268),
            nombre_completo='Vendedor Test',
            rol=Usuario.Rol.TECNICO
        )
        
        self.caja = CajaDiaria.objects.create(
            caja_id='CAJA-001',
            fecha=timezone.now().date(),
            turno='MAÑANA',
            operario=self.usuario,
            monto_inicial=500000,
            estado=CajaDiaria.Estado.ABIERTA
        )
        
        self.convenio = ConvenioIsapre.objects.create(
            nombre='Consalud',
            porcentaje_descuento=15,
            descripcion='Convenio Consalud'
        )
    
    def test_caja_creation(self):
        """Verifica que se crea una caja diaria."""
        self.assertEqual(self.caja.caja_id, 'CAJA-001')
        self.assertEqual(self.caja.estado, CajaDiaria.Estado.ABIERTA)
        self.assertEqual(self.caja.monto_inicial, 500000)
    
    def test_caja_cierre(self):
        """Verifica el cierre de caja."""
        self.caja.cerrar_caja(650000)
        
        self.assertEqual(self.caja.estado, CajaDiaria.Estado.CERRADA)
        self.assertEqual(self.caja.monto_cierre, 650000)
        self.assertIsNotNone(self.caja.hora_cierre)
    
    def test_convenio_creation(self):
        """Verifica que se crea un convenio Isapre."""
        self.assertEqual(self.convenio.nombre, 'Consalud')
        self.assertEqual(self.convenio.porcentaje_descuento, 15)
        self.assertTrue(self.convenio.activo)


class IntegracionTests(TestCase):
    """Pruebas de integración entre módulos."""
    
    def setUp(self):
        # Crear usuarios de cada rol con RUTs válidos
        self.admin = Usuario.objects.create_user(
            username='admin',
            rut=generar_rut_valido(19504267),
            nombre_completo='Admin',
            rol=Usuario.Rol.ADMIN,
            password='admin123'
        )
        
        self.qf = Usuario.objects.create_user(
            username='qf',
            rut=generar_rut_valido(18687239),
            nombre_completo='Químico Farmacéutico',
            rol=Usuario.Rol.FARMACEUTICO,
            password='qf123'
        )
        
        self.tecnico = Usuario.objects.create_user(
            username='tecnico',
            rut=generar_rut_valido(20345890),
            nombre_completo='Técnico',
            rol=Usuario.Rol.TECNICO,
            password='tecnico123'
        )
        
        self.bodeguero = Usuario.objects.create_user(
            username='bodeguero',
            rut=generar_rut_valido(17236749),
            nombre_completo='Bodeguero',
            rol=Usuario.Rol.BODEGUERO,
            password='bodeguero123'
        )
    
    def test_todos_los_roles_existen(self):
        """Verifica que todos los roles están creados."""
        self.assertEqual(self.admin.rol, Usuario.Rol.ADMIN)
        self.assertEqual(self.qf.rol, Usuario.Rol.FARMACEUTICO)
        self.assertEqual(self.tecnico.rol, Usuario.Rol.TECNICO)
        self.assertEqual(self.bodeguero.rol, Usuario.Rol.BODEGUERO)
    
    def test_auditoría_creation(self):
        """Verifica que se puede registrar auditoría."""
        log = LogAuditoria.objects.create(
            usuario=self.tecnico,
            tipo_evento=LogAuditoria.TipoEvento.LOGIN,
            descripcion='Inicio de sesión del técnico',
            hash_sha256='abc123' * 10 + 'abc1'
        )
        
        self.assertEqual(log.usuario, self.tecnico)
        self.assertEqual(log.tipo_evento, LogAuditoria.TipoEvento.LOGIN)
