"""Formularios para la aplicación de certificados"""
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


class ExcelImportForm(forms.Form):
    """Formulario para importar archivo Excel con participantes"""

    excel_file = forms.FileField(
        label="Archivo Excel",
        help_text="Seleccione un archivo Excel (.xlsx o .xls) con los datos de los participantes",
        widget=forms.FileInput(attrs={"accept": ".xlsx,.xls", "class": "form-control"}),
    )

    def clean_excel_file(self):
        """Valida el archivo Excel"""
        excel_file = self.cleaned_data.get("excel_file")

        if not excel_file:
            raise ValidationError("Debe seleccionar un archivo")

        # Validar extensión
        valid_extensions = [".xlsx", ".xls"]
        file_extension = excel_file.name.lower()[-5:]

        if not any(file_extension.endswith(ext) for ext in valid_extensions):
            raise ValidationError(
                "Formato de archivo no válido. Solo se permiten archivos .xlsx o .xls"
            )

        # Validar tamaño máximo (10MB)
        max_size = 10 * 1024 * 1024  # 10MB en bytes
        if excel_file.size > max_size:
            raise ValidationError(
                f"El archivo es demasiado grande. Tamaño máximo: 10MB. Tamaño actual: {excel_file.size / (1024 * 1024):.2f}MB"
            )

        return excel_file


class DNIQueryForm(forms.Form):
    """Formulario para consultar certificados por DNI"""

    dni = forms.CharField(
        label="DNI",
        max_length=8,
        min_length=1,
        help_text="Ingrese su número de DNI (hasta 8 dígitos)",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "12345678",
                "pattern": "[0-9]{1,8}",
            }
        ),
    )

    def clean_dni(self):
        """Valida y limpia el DNI, rellenando con ceros a la izquierda"""
        dni = self.cleaned_data.get("dni")

        if dni:
            # Eliminar espacios en blanco
            dni = dni.strip()

            # Validar que solo contenga dígitos
            if not dni.isdigit():
                raise ValidationError("El DNI solo debe contener números")

            # Validar longitud máxima
            if len(dni) > 8:
                raise ValidationError("El DNI no puede tener más de 8 dígitos")
            
            # Rellenar con ceros a la izquierda hasta 8 dígitos
            dni = dni.zfill(8)

        return dni
