"""
Formularios para la app recetas.
Validación de datos en formularios HTML tradicionales.
"""
from django import forms
from farmasur.models import Receta, RecetaRetenidaISP, UnidosisAsistencial


class RecetaForm(forms.ModelForm):
    """Formulario para crear/editar receta."""
    
    class Meta:
        model = Receta
        fields = [
            'folio', 'rut_paciente', 'nombre_paciente',
            'rut_medico', 'nombre_medico', 'fecha_emision',
            'medicamentos', 'notas_prescriptor', 'datos_adicionales'
        ]
        widgets = {
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
            'medicamentos': forms.Textarea(attrs={'rows': 4}),
            'notas_prescriptor': forms.Textarea(attrs={'rows': 3}),
        }


class RecetaAprobarForm(forms.Form):
    """Formulario para aprobar receta."""
    folio = forms.CharField(max_length=50, disabled=True)
    nombre_paciente = forms.CharField(max_length=255, disabled=True)
    confirmacion = forms.BooleanField(
        required=True,
        label='Confirmo la aprobación de esta receta'
    )


class RecetaRechazarForm(forms.Form):
    """Formulario para rechazar receta."""
    folio = forms.CharField(max_length=50, disabled=True)
    razon_rechazo = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Motivo del rechazo'
    )


class RecetaRetenidaISPForm(forms.ModelForm):
    """Formulario para registrar receta retenida ISP."""
    
    class Meta:
        model = RecetaRetenidaISP
        fields = [
            'numero_serie_carnet_paciente',
            'numero_serie_carnet_medico',
            'folio_isp'
        ]


class UnidosisAsistencialForm(forms.ModelForm):
    """Formulario para crear solicitud de unidosis."""
    
    class Meta:
        model = UnidosisAsistencial
        fields = [
            'folio',
            'numero_serie_carnet_paciente',
            'rut_paciente',
            'nombre_paciente',
            'medicamentos',
            'observaciones'
        ]
        widgets = {
            'medicamentos': forms.Textarea(attrs={'rows': 4}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }


class RecetaFilterForm(forms.Form):
    """Formulario para filtrar recetas."""
    estado = forms.ChoiceField(
        choices=[('', '--- Todos ---')] + list(Receta.Estado.choices),
        required=False
    )
    rut_paciente = forms.CharField(max_length=12, required=False, label='RUT paciente')
    rut_medico = forms.CharField(max_length=12, required=False, label='RUT médico')
    fecha_desde = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_hasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
