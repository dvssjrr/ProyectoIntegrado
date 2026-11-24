from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    """Permite autenticación con correo o nombre de usuario para compatibilidad."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        identificador = username or kwargs.get('email')
        if not identificador or not password:
            return None

        UserModel = get_user_model()
        coincidencias_email = UserModel.objects.filter(email__iexact=identificador).order_by('pk')
        user = coincidencias_email.first()
        if user and coincidencias_email.count() > 1:
            return None
        if user is None and '@' not in identificador:
            user = UserModel.objects.filter(username__iexact=identificador).first()
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
