"""
Formularios para la app ventas.
Validación de datos en formularios HTML tradicionales.
"""
from django import forms
from farmasur.models import CajaDiaria, POS, ConvenioIsapre, Comprobante


class CajaDiariaForm(forms.ModelForm):
    """Formulario para abrir caja diaria."""
    
    class Meta:
        model = CajaDiaria
        fields = ['caja_id', 'turno', 'monto_inicial']
        widgets = {
            'monto_inicial': forms.NumberInput(attrs={'min': '0'})
        }


class CajaCierreForm(forms.Form):
    """Formulario para cerrar caja."""
    monto_cierre = forms.IntegerField(
        min_value=0,
        label='Monto de Cierre (CLP)',
        widget=forms.NumberInput(attrs={'min': '0'})
    )
    notas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Notas del cierre'
    )


class POSForm(forms.ModelForm):
    """Formulario para crear venta POS."""
    
    class Meta:
        model = POS
        fields = [
            'rut_cliente', 'nombre_cliente', 'tipo_comprobante',
            'convenio_aplicado', 'requiere_receta_retenida',
            'requiere_unidosis', 'notas'
        ]


class ConvenioIsapreForm(forms.ModelForm):
    """Formulario para crear/editar convenio Isapre."""
    
    class Meta:
        model = ConvenioIsapre
        fields = [
            'nombre', 'descripcion', 'porcentaje_descuento',
            'monto_maximo_descuento', 'requiere_autorizacion_qf', 'activo'
        ]
        widgets = {
            'porcentaje_descuento': forms.NumberInput(attrs={'min': '0', 'max': '100'}),
            'monto_maximo_descuento': forms.NumberInput(attrs={'min': '0'}),
        }


class ComprobanteForm(forms.ModelForm):
    """Formulario para crear comprobante."""
    
    class Meta:
        model = Comprobante
        fields = [
            'tipo', 'folio_comprobante', 'rut_receptor',
            'nombre_receptor', 'giro_receptor', 'direccion_receptor'
        ]
