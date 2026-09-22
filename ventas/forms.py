# forms.py
from django import forms
# Se importan los modelos y la función de validación de RUT desde utils.py
from .models import Cliente, Producto
from .utils import validar_rut

# Clases Tailwind reutilizadas en todos los inputs para mantener
# la misma apariencia (fondo oscuro + borde neon al enfocar).
INPUT_CLASSES = (
    "w-full rounded-xl border border-slate-700 bg-slate-900/80 px-3 py-2.5 "
    "text-slate-100 shadow-sm outline-none transition duration-200 "
    "placeholder:text-slate-500 hover:border-slate-500 "
    "focus:border-cyan-400 focus:ring-4 focus:ring-cyan-400/20"
)

# Formulario para crear o editar un producto (incluye actualizar stock).
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["codigo", "nombre", "precio", "stock", "imagen"]
        widgets = {
            "codigo": forms.TextInput(attrs={
                "class": INPUT_CLASSES, "placeholder": "Ej. POL-001", "autocomplete": "off",
            }),
            "nombre": forms.TextInput(attrs={
                "class": INPUT_CLASSES, "placeholder": "Ej. Polera Estampada",
            }),
            "precio": forms.NumberInput(attrs={
                "class": INPUT_CLASSES, "placeholder": "0", "min": "0",
            }),
            "stock": forms.NumberInput(attrs={
                "class": INPUT_CLASSES, "placeholder": "0", "min": "0",
            }),
            "imagen": forms.ClearableFileInput(attrs={
                "class": "block w-full text-sm text-slate-300 file:mr-4 file:rounded-lg "
                         "file:border-0 file:bg-cyan-500/20 file:px-3 file:py-2 "
                         "file:text-cyan-300 file:font-semibold hover:file:bg-cyan-500/30",
            }),
        }
    # Se normaliza el código para evitar duplicados por mayúsculas/espacios.
    def clean_codigo(self):
        return self.cleaned_data["codigo"].strip().upper()


# Formulario de registro de venta, que valida stock y RUT, y opcionalmente guarda datos de clientes habituales.
class VentaForm(forms.Form):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(stock__gt=0),
        empty_label="Selecciona un producto",
        widget=forms.Select(attrs={"class": INPUT_CLASSES}),
    )
    cantidad = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": INPUT_CLASSES, "placeholder": "1"}),
    )
    rut_cliente = forms.CharField(
        label="RUT del cliente",
        widget=forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "12.345.678-9"}),
    )
    es_habitual = forms.BooleanField(
        label="¿Quiere ser cliente habitual?", required=False,
        widget=forms.CheckboxInput(attrs={
            "class": "size-5 rounded border-slate-600 bg-slate-900 text-cyan-400 "
                     "focus:ring-cyan-400/40",
        }),
    )
    nombre_cliente = forms.CharField(
        label="Nombre", required=False,
        widget=forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Nombre completo"}),
    )
    correo_cliente = forms.EmailField(
        label="Correo", required=False,
        widget=forms.EmailInput(attrs={"class": INPUT_CLASSES, "placeholder": "correo@ejemplo.com"}),
    )
    telefono_cliente = forms.CharField(
        label="Teléfono", required=False,
        widget=forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "+56 9 1234 5678"}),
    )
    # Validación del RUT y de los datos de clientes habituales.
    def clean_rut_cliente(self):
        rut = self.cleaned_data["rut_cliente"]
        if not validar_rut(rut):
            raise forms.ValidationError("El RUT ingresado no es válido.")
        return rut
    # Validación de stock y de campos obligatorios para clientes habituales.
    def clean(self):
        datos = super().clean()
        if datos.get("es_habitual"):
            if not datos.get("nombre_cliente"):
                self.add_error("nombre_cliente", "Requerido para clientes habituales.")
            if not datos.get("correo_cliente"):
                self.add_error("correo_cliente", "Requerido para clientes habituales.")

        producto = datos.get("producto")
        cantidad = datos.get("cantidad")
        if producto and cantidad and cantidad > producto.stock:
            raise forms.ValidationError(
                f"Stock insuficiente: quedan {producto.stock} unidades de {producto.nombre}."
            )
        return datos

# Reservado para editar clientes habituales desde su ficha.
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["rut", "nombre", "correo", "telefono"]
        widgets = {
            "rut": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "nombre": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "correo": forms.EmailInput(attrs={"class": INPUT_CLASSES}),
            "telefono": forms.TextInput(attrs={"class": INPUT_CLASSES}),
        }