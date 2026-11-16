"""
Capa de Formularios
Formularios Django para validación en templates
"""

from farmasur.forms.usuarios.forms import UsuarioForm
from farmasur.forms.inventario.forms import MedicamentoForm
from farmasur.forms.recetas.forms import RecetaForm
from farmasur.forms.ventas.forms import VentaForm

__all__ = [
    'UsuarioForm',
    'MedicamentoForm',
    'RecetaForm',
    'VentaForm',
]
