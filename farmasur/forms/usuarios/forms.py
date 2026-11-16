"""
Formularios para la app usuarios.
Validación de datos en formularios HTML tradicionales.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from farmasur.models import Usuario
from farmasur.validators import validar_rut_chileno


class UsuarioCreationForm(UserCreationForm):
    """Formulario para crear un nuevo usuario."""
    rut = forms.CharField(
        max_length=12,
        required=True,
        validators=[validar_rut_chileno],
        widget=forms.TextInput(attrs={'placeholder': 'XX.XXX.XXX-K'})
    )
    nombre_completo = forms.CharField(max_length=255, required=True)
    rol = forms.ChoiceField(choices=Usuario.Rol.choices)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'nombre_completo', 'rut', 'rol', 'password1', 'password2')


class UsuarioChangeForm(UserChangeForm):
    """Formulario para editar un usuario existente."""
    rut = forms.CharField(
        max_length=12,
        required=False,
        validators=[validar_rut_chileno]
    )
    
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'nombre_completo', 'rut', 'rol', 'activo')


class UsuarioFilterForm(forms.Form):
    """Formulario para filtrar usuarios."""
    rol = forms.ChoiceField(
        choices=[('', '--- Todos los roles ---')] + list(Usuario.Rol.choices),
        required=False
    )
    activo = forms.NullBooleanField(
        required=False,
        label='Estado',
        widget=forms.Select(choices=[
            ('', '--- Todos ---'),
            (True, 'Activo'),
            (False, 'Inactivo')
        ])
    )
    busqueda = forms.CharField(max_length=100, required=False, label='Buscar por nombre o RUT')
