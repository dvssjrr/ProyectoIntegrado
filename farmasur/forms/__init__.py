"""
Capa de Formularios
Formularios Django para validación en templates
"""

from farmasur.forms.usuarios.forms import UsuarioCreationForm, UsuarioChangeForm, UsuarioFilterForm
from farmasur.forms.inventario.forms import LoteForm, MermaForm, ProductoFilterForm
from farmasur.forms.recetas.forms import RecetaForm
from farmasur.forms.ventas.forms import POSForm

__all__ = [
    'UsuarioCreationForm',
    'UsuarioChangeForm',
    'UsuarioFilterForm',
    'LoteForm',
    'MermaForm',
    'ProductoFilterForm',
    'RecetaForm',
    'POSForm',
]
