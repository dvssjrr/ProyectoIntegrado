"""
Capa de Formularios
Formularios Django para validación en templates
"""

from farmasur.forms.usuarios.forms import UsuarioForm
from farmasur.forms.inventario.forms import LoteForm, MermaForm, ProductoFilterForm
from farmasur.forms.recetas.forms import RecetaForm
from farmasur.forms.ventas.forms import VentaForm

__all__ = [
    'UsuarioForm',
    'LoteForm',
    'MermaForm',
    'ProductoFilterForm',
    'RecetaForm',
    'VentaForm',
]
