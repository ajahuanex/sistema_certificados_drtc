"""Tests para formularios"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from certificates.forms import ExcelImportForm, DNIQueryForm
from io import BytesIO
from openpyxl import Workbook


class ExcelImportFormTest(TestCase):
    """Tests para ExcelImportForm"""

    def _create_excel_file(self, filename="test.xlsx"):
        """Helper para crear un archivo Excel de prueba"""
        workbook = Workbook()
        sheet = workbook.active
        sheet["A1"] = "Test"

        excel_buffer = BytesIO()
        workbook.save(excel_buffer)
        excel_buffer.seek(0)

        return SimpleUploadedFile(
            filename, excel_buffer.read(), content_type="application/vnd.ms-excel"
        )

    def test_form_with_valid_xlsx_file(self):
        """Debe aceptar archivo .xlsx válido"""
        excel_file = self._create_excel_file("test.xlsx")

        form = ExcelImportForm(files={"excel_file": excel_file})

        self.assertTrue(form.is_valid())

    def test_form_with_valid_xls_file(self):
        """Debe aceptar archivo .xls válido"""
        excel_file = self._create_excel_file("test.xls")

        form = ExcelImportForm(files={"excel_file": excel_file})

        self.assertTrue(form.is_valid())

    def test_form_with_invalid_extension(self):
        """Debe rechazar archivos con extensión inválida"""
        invalid_file = SimpleUploadedFile(
            "test.txt", b"test content", content_type="text/plain"
        )

        form = ExcelImportForm(files={"excel_file": invalid_file})

        self.assertFalse(form.is_valid())
        self.assertIn("excel_file", form.errors)
        self.assertIn("Formato de archivo no válido", str(form.errors["excel_file"]))

    def test_form_with_file_too_large(self):
        """Debe rechazar archivos mayores a 10MB"""
        # Crear archivo grande (11MB)
        large_content = b"x" * (11 * 1024 * 1024)
        large_file = SimpleUploadedFile(
            "large.xlsx", large_content, content_type="application/vnd.ms-excel"
        )

        form = ExcelImportForm(files={"excel_file": large_file})

        self.assertFalse(form.is_valid())
        self.assertIn("excel_file", form.errors)
        self.assertIn("demasiado grande", str(form.errors["excel_file"]))

    def test_form_without_file(self):
        """Debe rechazar formulario sin archivo"""
        form = ExcelImportForm(files={})

        self.assertFalse(form.is_valid())
        self.assertIn("excel_file", form.errors)


class DNIQueryFormTest(TestCase):
    """Tests para DNIQueryForm"""

    def test_form_with_valid_dni(self):
        """Debe aceptar DNI válido de 8 dígitos"""
        form = DNIQueryForm(data={"dni": "12345678"})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["dni"], "12345678")

    def test_form_with_dni_with_spaces(self):
        """Debe limpiar espacios en blanco del DNI"""
        form = DNIQueryForm(data={"dni": " 12345678 "})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["dni"], "12345678")

    def test_form_with_dni_too_short(self):
        """Debe rechazar DNI con menos de 8 dígitos"""
        form = DNIQueryForm(data={"dni": "1234567"})

        self.assertFalse(form.is_valid())
        self.assertIn("dni", form.errors)

    def test_form_with_dni_too_long(self):
        """Debe rechazar DNI con más de 8 dígitos"""
        form = DNIQueryForm(data={"dni": "123456789"})

        self.assertFalse(form.is_valid())
        self.assertIn("dni", form.errors)

    def test_form_with_dni_with_letters(self):
        """Debe rechazar DNI con letras"""
        form = DNIQueryForm(data={"dni": "1234567A"})

        self.assertFalse(form.is_valid())
        self.assertIn("dni", form.errors)

    def test_form_with_dni_with_special_characters(self):
        """Debe rechazar DNI con caracteres especiales"""
        form = DNIQueryForm(data={"dni": "12345-78"})

        self.assertFalse(form.is_valid())
        self.assertIn("dni", form.errors)

    def test_form_without_dni(self):
        """Debe rechazar formulario sin DNI"""
        form = DNIQueryForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn("dni", form.errors)

    def test_form_with_empty_dni(self):
        """Debe rechazar DNI vacío"""
        form = DNIQueryForm(data={"dni": ""})

        self.assertFalse(form.is_valid())
        self.assertIn("dni", form.errors)
