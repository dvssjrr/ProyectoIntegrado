"""
Formularios para la app inventario.
Validación de datos en formularios HTML tradicionales.
"""
from django import forms
from farmasur.models import Lote, Producto, Merma


class LoteForm(forms.ModelForm):
    """Formulario para crear/editar un lote."""
    
    class Meta:
        model = Lote
        fields = [
            'producto', 'codigo_lote', 'fecha_vencimiento',
            'stock_vitrina', 'stock_bodega', 'costo_compra'
        ]
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
            'codigo_lote': forms.TextInput(attrs={'placeholder': 'Ej: LOTE-2026-001'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        from datetime import date
        fecha_vencimiento = cleaned_data.get('fecha_vencimiento')
        
        if fecha_vencimiento and fecha_vencimiento < date.today():
            raise forms.ValidationError("La fecha de vencimiento no puede ser en el pasado.")
        
        return cleaned_data


class MermaForm(forms.ModelForm):
    """Formulario para registrar una merma (pérdida de medicamentos)."""
    
    class Meta:
        model = Merma
        fields = ['lote', 'cantidad', 'razon', 'descripcion']
    
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        lote = self.cleaned_data.get('lote')
        
        if lote and cantidad is not None:
            stock_total = lote.stock_vitrina + lote.stock_bodega
            if cantidad > stock_total:
                raise forms.ValidationError(
                    f"La cantidad no puede exceder el stock del lote ({stock_total})."
                )
        
        return cantidad


class ProductoFilterForm(forms.Form):
    """Formulario para filtrar productos."""
    laboratorio = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label='Todos los laboratorios'
    )
    activo = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=[
            ('', '--- Todos ---'),
            (True, 'Activo'),
            (False, 'Inactivo')
        ])
    )
    busqueda = forms.CharField(max_length=100, required=False, label='Buscar por nombre o código')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from farmasur.models import Laboratorio
        self.fields['laboratorio'].queryset = Laboratorio.objects.all()
