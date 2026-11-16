from django import forms

from farmasur.models.inventario.models import Laboratorio, Lote, Merma, Producto
from farmasur.models.usuarios.models import Usuario
from farmasur.models.ventas.models import ConvenioIsapre


class BootstrapMixin:
    def _estilizar(self):
        for campo in self.fields.values():
            w = campo.widget
            if isinstance(w, forms.CheckboxInput):
                w.attrs['class'] = 'form-check-input'
            elif isinstance(w, forms.Select):
                w.attrs['class'] = 'form-select'
            else:
                w.attrs['class'] = 'form-control'


class BForm(BootstrapMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._estilizar()


class BModelForm(BootstrapMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._estilizar()


def _fecha():
    return forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')


class ProductoForm(BModelForm):
    class Meta:
        model = Producto
        fields = ['sku_codigo_barra', 'nombre_comercial', 'principio_activo', 'presentacion',
                  'categoria', 'laboratorio', 'condicion_venta', 'precio_clp',
                  'stock_minimo_vitrina', 'requiere_cadena_frio', 'activo']


class LoteForm(BModelForm):
    class Meta:
        model = Lote
        fields = ['producto', 'codigo_lote', 'fecha_vencimiento', 'stock_vitrina',
                  'stock_bodega', 'costo_compra']
        widgets = {'fecha_vencimiento': _fecha()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(activo=True)


class LaboratorioForm(BModelForm):
    class Meta:
        model = Laboratorio
        fields = ['nombre', 'pais', 'telefono', 'email', 'contacto']


class ConvenioForm(BModelForm):
    class Meta:
        model = ConvenioIsapre
        fields = ['nombre', 'descripcion', 'porcentaje_descuento',
                  'monto_maximo_descuento', 'requiere_autorizacion_qf', 'activo']
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 2})}


class MermaWebForm(BForm):
    lote = forms.ModelChoiceField(Lote.objects.none())
    cantidad = forms.IntegerField(min_value=1)
    razon = forms.ChoiceField(choices=Merma.Razon.choices, label='Razón')
    descripcion = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lote'].queryset = Lote.objects.filter(activo=True).select_related('producto')


class TransferirForm(BForm):
    producto = forms.ModelChoiceField(Producto.objects.none())
    cantidad = forms.IntegerField(min_value=1)
    origen = forms.ChoiceField(choices=[('BODEGA', 'Bodega'), ('VITRINA', 'Vitrina')], initial='BODEGA')
    destino = forms.ChoiceField(choices=[('VITRINA', 'Vitrina'), ('BODEGA', 'Bodega')], initial='VITRINA')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(activo=True)


class RecetaWebForm(BForm):
    rut_paciente = forms.CharField(max_length=12, label='RUT paciente')
    nombre_paciente = forms.CharField(max_length=255)
    rut_medico = forms.CharField(max_length=12, label='RUT médico')
    nombre_medico = forms.CharField(max_length=255, label='Nombre médico')
    fecha_emision = forms.DateField(widget=_fecha(), label='Fecha de emisión')
    producto = forms.ModelChoiceField(Producto.objects.none())
    cantidad = forms.IntegerField(min_value=1, initial=1)
    instrucciones = forms.CharField(max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.filter(activo=True).exclude(
            condicion_venta=Producto.CondicionVenta.LIBRE)

    def _rut(self, campo):
        valido, msg = Usuario.validar_rut(self.cleaned_data[campo])
        if not valido:
            raise forms.ValidationError(msg)
        return self.cleaned_data[campo]

    def clean_rut_paciente(self):
        return self._rut('rut_paciente')

    def clean_rut_medico(self):
        return self._rut('rut_medico')


class RechazoForm(BForm):
    razon = forms.CharField(max_length=255, label='Motivo del rechazo')


class AbrirCajaForm(BForm):
    caja_id = forms.CharField(max_length=50, initial='CAJA-01', label='Caja')
    turno = forms.ChoiceField(choices=[('MAÑANA', 'Mañana'), ('TARDE', 'Tarde'), ('NOCHE', 'Noche')])
    monto_inicial = forms.IntegerField(min_value=0, label='Monto inicial (CLP)')


class CerrarCajaForm(BForm):
    monto_cierre = forms.IntegerField(min_value=0, label='Monto contado (CLP)')
    notas = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))


class VentaForm(BForm):
    LINEAS = 5
    tipo_comprobante = forms.ChoiceField(choices=[('BOLETA', 'Boleta'), ('FACTURA', 'Factura'), ('VOUCHER', 'Voucher')])
    rut_cliente = forms.CharField(max_length=12, required=False)
    nombre_cliente = forms.CharField(max_length=255, required=False)
    convenio = forms.ModelChoiceField(ConvenioIsapre.objects.none(), required=False, label='Convenio / Isapre')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['convenio'].queryset = ConvenioIsapre.objects.filter(activo=True)
        productos = Producto.objects.filter(activo=True).order_by('nombre_comercial')
        for i in range(self.LINEAS):
            self.fields[f'producto_{i}'] = forms.ModelChoiceField(
                productos, required=False, label=f'Producto {i + 1}')
            self.fields[f'cantidad_{i}'] = forms.IntegerField(
                min_value=1, required=False, label='Cantidad')
        self._estilizar()

    def lineas(self):
        return [(self[f'producto_{i}'], self[f'cantidad_{i}']) for i in range(self.LINEAS)]

    def clean(self):
        datos = super().clean()
        items = []
        for i in range(self.LINEAS):
            prod, cant = datos.get(f'producto_{i}'), datos.get(f'cantidad_{i}')
            if prod and cant:
                items.append({'sku': prod.sku_codigo_barra, 'nombre': prod.nombre_comercial,
                              'cantidad': cant, 'precio_unitario': prod.precio_clp})
            elif prod or cant:
                raise forms.ValidationError(f'Completa producto y cantidad en la línea {i + 1}.')
        if not items:
            raise forms.ValidationError('Agrega al menos un producto.')
        datos['items'] = items
        return datos


class UsuarioWebForm(BForm):
    username = forms.CharField(max_length=150, label='Usuario')
    nombre_completo = forms.CharField(max_length=255)
    rut = forms.CharField(max_length=12)
    email = forms.EmailField(required=False)
    rol = forms.ChoiceField(choices=Usuario.Rol.choices)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8, label='Contraseña')

    def clean_rut(self):
        valido, msg = Usuario.validar_rut(self.cleaned_data['rut'])
        if not valido:
            raise forms.ValidationError(msg)
        rut = msg
        if Usuario.objects.filter(rut=rut).exists():
            raise forms.ValidationError('Ya existe un usuario con ese RUT.')
        return rut

    def clean_username(self):
        if Usuario.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError('Ese nombre de usuario ya existe.')
        return self.cleaned_data['username']
