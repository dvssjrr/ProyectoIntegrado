from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from farmasur.models.inventario.models import Lote, Merma, Producto
from farmasur.models.recetas.models import Receta
from farmasur.models.usuarios.models import Usuario
from farmasur.models.ventas.models import CajaDiaria, POS

RUTS = {
    Usuario.Rol.ADMIN: '11111111-1',
    Usuario.Rol.FARMACEUTICO: '12345678-5',
    Usuario.Rol.TECNICO: '22222222-2',
    Usuario.Rol.BODEGUERO: '33333333-3',
}
PAGINAS = ['inicio', 'productos', 'producto_nuevo', 'inventario', 'lote_nuevo', 'transferir', 'mermas',
           'merma_nueva', 'libro', 'receta_nueva', 'pos', 'caja', 'configuracion', 'usuario_nuevo',
           'laboratorio_nuevo', 'convenio_nuevo']


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
            'username': 'nuevo', 'nombre_completo': 'Nuevo Usuario', 'rut': '2277185-K',
            'rol': 'TECNICO', 'password': 'clave12345'})
        self.assertRedirects(resp, reverse('configuracion'))
        self.assertTrue(Usuario.objects.filter(username='nuevo', rut='2277185K').exists())
