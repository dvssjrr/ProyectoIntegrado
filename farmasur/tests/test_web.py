import json

from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from farmasur.models.inventario.models import Lote, Merma, Producto
from farmasur.models.recetas.models import Receta
from farmasur.models.usuarios.models import LogAuditoria, Usuario
from farmasur.models.ventas.models import CajaDiaria, Cliente, POS
from farmasur.services.ventas.services import POSService

RUTS = {
    Usuario.Rol.ADMIN: '11111111-1',
    Usuario.Rol.FARMACEUTICO: '12345678-5',
    Usuario.Rol.TECNICO: '22222222-2',
    Usuario.Rol.BODEGUERO: '33333333-3',
}
PAGINAS = ['inicio', 'productos', 'producto_nuevo', 'inventario', 'lote_nuevo', 'transferir', 'mermas',
           'merma_nueva', 'libro', 'receta_nueva', 'pos', 'caja', 'configuracion', 'usuario_nuevo',
           'laboratorio_nuevo', 'convenio_nuevo', 'reportes_ventas', 'auditoria', 'clientes']


class WebTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usuarios = {
            rol: Usuario.objects.create_user(username=f'u_{rol}', password='x', rut=rut,
                                             nombre_completo=f'Usuario {rol}', rol=rol)
            for rol, rut in RUTS.items()}
        call_command('cargar_datos_ejemplo', verbosity=0)

    def entrar(self, rol=Usuario.Rol.ADMIN):
        self.client.force_login(self.usuarios[rol])

    def test_login_publico_y_redirige_anonimos(self):
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)
        self.assertEqual(self.client.get(reverse('inicio')).status_code, 302)

    def test_un_usuario_puede_iniciar_sesion_en_sesiones_simultaneas(self):
        credenciales = {'username': self.usuarios[Usuario.Rol.ADMIN].username, 'password': 'x'}
        ventana_uno = Client()
        ventana_dos = Client()

        self.assertTrue(ventana_uno.login(**credenciales))
        self.assertTrue(ventana_dos.login(**credenciales))
        self.assertEqual(ventana_uno.get(reverse('inicio')).status_code, 200)
        self.assertEqual(ventana_dos.get(reverse('inicio')).status_code, 200)

    def test_abrir_otra_ventana_a_isla_la_sesion(self):
        ventana_uno = Client(enforce_csrf_checks=True)
        ventana_uno.force_login(self.usuarios[Usuario.Rol.ADMIN])
        pagina_uno = ventana_uno.get(reverse('inicio'))
        self.assertContains(pagina_uno, 'Usuario ADMIN')

        ventana_dos = ventana_uno
        nueva_ventana = ventana_dos.get('/__new-window__/')
        self.assertEqual(nueva_ventana.status_code, 302)
        url_login = nueva_ventana['Location']
        self.assertRegex(url_login, r'^/_window/[0-9a-f]{32}/login/$')

        pagina_login = ventana_dos.get(url_login)
        csrf_token = pagina_login.context['csrf_token']
        respuesta = ventana_dos.post(url_login, {
            'username': self.usuarios[Usuario.Rol.TECNICO].username,
            'password': 'x',
            'csrfmiddlewaretoken': csrf_token,
        }, follow=True)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Usuario TECNICO')
        self.assertContains(respuesta, 'Abrir sesión con otro usuario')
        self.assertContains(respuesta, f'href="{url_login.rsplit("login/", 1)[0]}productos/"')

        pagina_uno = ventana_uno.get(reverse('inicio'))
        self.assertContains(pagina_uno, 'Usuario ADMIN')
        self.assertNotContains(pagina_uno, 'Usuario TECNICO')

        logout = ventana_dos.post(
            url_login.replace('/login/', '/logout/'),
            {'csrfmiddlewaretoken': respuesta.context['csrf_token']},
        )
        self.assertEqual(logout.status_code, 302)
        pagina_uno = ventana_uno.get(reverse('inicio'))
        self.assertContains(pagina_uno, 'Usuario ADMIN')

    def test_admin_ve_todas_las_paginas(self):
        self.entrar()
        for nombre in PAGINAS:
            with self.subTest(pagina=nombre):
                self.assertEqual(self.client.get(reverse(nombre)).status_code, 200)

    def test_permisos_por_rol(self):
        self.entrar(Usuario.Rol.TECNICO)
        self.assertEqual(self.client.get(reverse('mermas')).status_code, 403)
        self.assertEqual(self.client.get(reverse('configuracion')).status_code, 403)
        self.assertEqual(self.client.get(reverse('pos')).status_code, 200)
        self.client.logout()
        self.entrar(Usuario.Rol.BODEGUERO)
        self.assertEqual(self.client.get(reverse('pos')).status_code, 403)
        self.assertEqual(self.client.get(reverse('lote_nuevo')).status_code, 200)

    def test_crear_producto(self):
        self.entrar(Usuario.Rol.BODEGUERO)
        lab = Producto.objects.first().laboratorio
        resp = self.client.post(reverse('producto_nuevo'), {
            'sku_codigo_barra': '7809999999991', 'nombre_comercial': 'Nuevo', 'principio_activo': 'X',
            'presentacion': 'Caja', 'categoria': 'OTRO', 'laboratorio': lab.pk,
            'condicion_venta': 'LIBRE', 'precio_clp': 1000, 'stock_minimo_vitrina': 5, 'activo': 'on'})
        self.assertRedirects(resp, reverse('productos'))
        self.assertTrue(Producto.objects.filter(sku_codigo_barra='7809999999991').exists())

    def test_venta_descuenta_stock(self):
        self.entrar(Usuario.Rol.TECNICO)
        producto = Producto.objects.get(sku_codigo_barra='7800000000011')
        antes = sum(l.stock_vitrina + l.stock_bodega for l in producto.lotes.all())
        datos = {'tipo_comprobante': 'BOLETA', 'producto_0': producto.pk, 'cantidad_0': 3}
        resp = self.client.post(reverse('pos'), datos)
        self.assertRedirects(resp, reverse('pos'))
        despues = sum(l.stock_vitrina + l.stock_bodega for l in producto.lotes.all())
        self.assertEqual(antes - 3, despues)
        self.assertEqual(POS.objects.count(), 2)

    def test_merma_y_movimiento(self):
        self.entrar(Usuario.Rol.BODEGUERO)
        lote = Lote.objects.filter(stock_bodega__gt=0, codigo_lote__endswith='-1').first()
        vit, bod = lote.stock_vitrina, lote.stock_bodega
        self.client.post(reverse('merma_nueva'), {'lote': lote.pk, 'cantidad': 4, 'razon': 'DAÑO'})
        lote.refresh_from_db()
        self.assertEqual(lote.stock_vitrina + lote.stock_bodega, vit + bod - 4)
        self.assertEqual(Merma.objects.filter(cantidad=4).count(), 1)
        resp = self.client.post(reverse('merma_nueva'), {'lote': lote.pk, 'cantidad': 99999, 'razon': 'DAÑO'})
        self.assertEqual(resp.status_code, 200)

    def test_flujo_receta_y_caja(self):
        self.entrar(Usuario.Rol.FARMACEUTICO)
        receta = Receta.objects.get(folio='R-0001')
        self.client.post(reverse('receta_accion', args=[receta.pk, 'aprobar']))
        receta.refresh_from_db()
        self.assertEqual(receta.estado, 'APROBADA')
        resp = self.client.post(reverse('caja'), {'abrir': '1', 'abrir-caja_id': 'CAJA-02',
                                                  'abrir-turno': 'TARDE', 'abrir-monto_inicial': 1000})
        self.assertRedirects(resp, reverse('caja'))
        caja = CajaDiaria.objects.get(caja_id='CAJA-02')
        self.client.post(reverse('caja'), {'cerrar': '1', 'caja_pk': caja.pk, 'cerrar-monto_cierre': 1000})
        caja.refresh_from_db()
        self.assertEqual(caja.estado, 'CERRADA')

    def test_admin_crea_usuario(self):
        self.entrar()
        resp = self.client.post(reverse('usuario_nuevo'), {
            'username': 'nuevo', 'nombre_completo': 'Nuevo Usuario', 'rut': '2.277.185-k',
            'email': 'nuevo@gmail.com', 'rol': 'TECNICO', 'password': 'clave12345'})
        self.assertRedirects(resp, reverse('configuracion'))
        self.assertTrue(Usuario.objects.filter(
            username='nuevo', rut='2277185K', email='nuevo@gmail.com'
        ).exists())

    def test_admin_accede_a_reportes_auditoria_y_clientes(self):
        self.entrar()
        for nombre in ('reportes_ventas', 'auditoria', 'clientes'):
            with self.subTest(pagina=nombre):
                self.assertEqual(self.client.get(reverse(nombre)).status_code, 200)

    def test_login_con_correo_genera_auditoria_con_identidad_e_ip(self):
        usuario = self.usuarios[Usuario.Rol.ADMIN]
        usuario.email = 'admin@gmail.com'
        usuario.save()
        respuesta = self.client.post(reverse('login'), {
            'username': usuario.email, 'password': 'x',
        })
        self.assertEqual(respuesta.status_code, 302)
        evento = LogAuditoria.objects.get(usuario=usuario, tipo_evento=LogAuditoria.TipoEvento.LOGIN)
        self.assertEqual(evento.direccion_ip, '127.0.0.1')
        self.assertEqual(evento.datos_adicionales['rut'], usuario.rut)
        self.assertEqual(evento.datos_adicionales['nombre_completo'], usuario.nombre_completo)

    def test_admin_no_puede_editar_otra_cuenta_admin(self):
        self.entrar()
        usuario_admin = self.usuarios[Usuario.Rol.ADMIN]
        respuesta = self.client.get(reverse('usuario_editar', args=[usuario_admin.pk]))
        self.assertEqual(respuesta.status_code, 403)
        api_respuesta = self.client.patch(
            reverse('usuario-detail', args=[usuario_admin.pk]),
            data=json.dumps({'nombre_completo': 'Cambio no autorizado'}),
            content_type='application/json',
        )
        self.assertEqual(api_respuesta.status_code, 403)

    def test_registrar_ficha_de_cliente_separada_de_empleados(self):
        self.entrar()
        respuesta = self.client.post(reverse('cliente_nuevo'), {
            'rut': '2.277.185-k', 'nombre_completo': 'Cliente de prueba',
            'email': 'cliente@gmail.com', 'telefono': '912345678', 'convenio': '',
        })
        self.assertRedirects(respuesta, reverse('clientes'))
        cliente = Cliente.objects.get(rut='2277185K', nombre_completo='Cliente de prueba')
        historial = self.client.get(reverse('historial_compras_cliente', args=[cliente.pk]))
        self.assertEqual(historial.status_code, 200)
        self.client.logout()
        self.entrar(Usuario.Rol.TECNICO)
        ficha = self.client.get(reverse('buscar_cliente_rut'), {'rut': '2.277.185-k'})
        self.assertEqual(ficha.status_code, 200)
        self.assertEqual(ficha.json()['nombre'], cliente.nombre_completo)
        self.assertEqual(ficha.json()['compras'], 0)

    def test_pago_tarjeta_se_guarda_como_simulacion_banco_estado(self):
        self.entrar(Usuario.Rol.TECNICO)
        producto = Producto.objects.get(sku_codigo_barra='7800000000011')
        respuesta = self.client.post(reverse('pos'), {
            'tipo_comprobante': 'BOLETA', 'producto_0': producto.pk, 'cantidad_0': 1,
            'medio_pago': 'TARJETA', 'banco_tarjeta': 'BANCO_ESTADO',
        })
        self.assertEqual(respuesta.status_code, 302)
        venta = POS.objects.latest('id')
        self.assertEqual(venta.metodo_pago, POS.MetodoPago.TARJETA)
        self.assertEqual(venta.banco_tarjeta, 'BANCO_ESTADO')
        self.assertTrue(venta.referencia_pago.startswith('SIM-'))

    def test_caja_muestra_resumen_de_medios_de_pago(self):
        self.entrar(Usuario.Rol.FARMACEUTICO)
        respuesta = self.client.get(reverse('caja'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Por medio:')

    def test_venta_con_receta_exige_autorizacion_de_quimico_farmaceutico(self):
        self.entrar(Usuario.Rol.TECNICO)
        producto = Producto.objects.get(sku_codigo_barra='7800000000042')
        caja = CajaDiaria.objects.filter(estado=CajaDiaria.Estado.ABIERTA).first()
        self.assertIsNotNone(caja)
        with self.assertRaisesMessage(ValueError, 'Químico Farmacéutico'):
            POSService.crear_venta(
                caja=caja, folio='V-TEST-RECETA', operario=self.usuarios[Usuario.Rol.TECNICO],
                items=[{'sku': producto.sku_codigo_barra, 'cantidad': 1,
                        'precio_unitario': producto.precio_clp}],
                receta_folio='RECETA-TEST', confirmacion_qf=True,
                autorizado_por_qf=self.usuarios[Usuario.Rol.TECNICO],
            )

    def test_quimico_confirma_receta_aprobada_y_rut_del_paciente(self):
        qf = self.usuarios[Usuario.Rol.FARMACEUTICO]
        producto = Producto.objects.get(sku_codigo_barra='7800000000042')
        caja = CajaDiaria.objects.filter(estado=CajaDiaria.Estado.ABIERTA).first()
        receta = Receta.objects.create(
            folio='RECETA-QF-TEST', rut_paciente=qf.rut, nombre_paciente=qf.nombre_completo,
            rut_medico='11111111-1', nombre_medico='Medico de prueba',
            fecha_emision=timezone.localdate(), estado=Receta.Estado.APROBADA,
            medicamentos=[{'sku': producto.sku_codigo_barra, 'cantidad': 1}],
        )
        argumentos = {
            'caja': caja, 'folio': 'VENTA-QF-TEST', 'operario': qf,
            'items': [{'sku': producto.sku_codigo_barra, 'cantidad': 1,
                       'precio_unitario': producto.precio_clp}],
            'rut_cliente': qf.rut, 'nombre_cliente': qf.nombre_completo,
            'receta_folio': receta.folio, 'autorizado_por_qf': qf, 'confirmacion_qf': True,
        }
        with self.assertRaisesMessage(ValueError, 'RUT del cliente'):
            POSService.crear_venta(**{**argumentos, 'rut_cliente': '99999999-9'})
        venta = POSService.crear_venta(**argumentos)
        self.assertEqual(venta.receta, receta)
        self.assertEqual(venta.autorizado_por_qf, qf)

    def test_buscar_producto_para_lector_usa_codigo_exacto(self):
        self.entrar(Usuario.Rol.TECNICO)
        codigo = '7800000000011'

        respuesta = self.client.get(reverse('buscar_producto_codigo'), {'codigo': codigo})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()['sku'], codigo)

        parcial = self.client.get(reverse('buscar_producto_codigo'), {'codigo': codigo[:-1]})
        self.assertEqual(parcial.status_code, 404)
