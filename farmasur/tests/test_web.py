from django.test import TestCase
from django.urls import reverse

from farmasur.models.usuarios.models import Usuario

RUTS = {
    Usuario.Rol.ADMIN: '11111111-1',
    Usuario.Rol.FARMACEUTICO: '12345678-5',
    Usuario.Rol.TECNICO: '22222222-2',
    Usuario.Rol.BODEGUERO: '33333333-3',
}


class PanelesWebTests(TestCase):
    def _usuario(self, rol):
        return Usuario.objects.create_user(
            username=f'u_{rol}', password='x', rut=RUTS[rol],
            nombre_completo=f'Usuario {rol}', rol=rol,
        )

    def test_login_publico(self):
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)

    def test_cada_rol_va_a_su_panel(self):
        for rol in RUTS:
            with self.subTest(rol=rol):
                self.client.force_login(self._usuario(rol))
                resp = self.client.get(reverse('inicio'), follow=True)
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(resp.redirect_chain[-1][0], reverse(f'panel_{rol.lower()}'))
                self.client.logout()

    def test_rol_no_accede_a_panel_ajeno(self):
        self.client.force_login(self._usuario(Usuario.Rol.TECNICO))
        self.assertEqual(self.client.get(reverse('panel_bodeguero')).status_code, 403)
