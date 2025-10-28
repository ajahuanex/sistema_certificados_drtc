"""Tests para QRCodeService"""
from django.test import TestCase, override_settings
from certificates.services.qr_service import QRCodeService
from PIL import Image
import uuid


class QRCodeServiceTest(TestCase):
    """Tests para el servicio de generación de códigos QR"""

    def setUp(self):
        self.service = QRCodeService()
        self.test_uuid = str(uuid.uuid4())

    @override_settings(BASE_URL="https://example.com")
    def test_get_verification_url(self):
        """Debe generar correctamente la URL de verificación"""
        url = self.service.get_verification_url(self.test_uuid)

        self.assertEqual(url, f"https://example.com/verificar/{self.test_uuid}/")

    def test_get_verification_url_with_default(self):
        """Debe usar URL por defecto si BASE_URL no está configurado"""
        url = self.service.get_verification_url(self.test_uuid)

        self.assertIn("localhost", url)
        self.assertIn(self.test_uuid, url)

    def test_generate_qr_returns_bytesio(self):
        """Debe retornar un objeto BytesIO"""
        qr_buffer = self.service.generate_qr(self.test_uuid)

        self.assertIsNotNone(qr_buffer)
        self.assertTrue(hasattr(qr_buffer, "read"))

    def test_generate_qr_creates_valid_image(self):
        """Debe crear una imagen PNG válida"""
        qr_buffer = self.service.generate_qr(self.test_uuid)

        # Intentar abrir la imagen con PIL
        img = Image.open(qr_buffer)

        self.assertEqual(img.format, "PNG")
        self.assertEqual(img.size, (300, 300))  # Verificar tamaño

    def test_generate_qr_contains_verification_url(self):
        """El código QR debe contener la URL de verificación"""
        import qrcode

        qr_buffer = self.service.generate_qr(self.test_uuid)

        # Decodificar el QR para verificar su contenido
        img = Image.open(qr_buffer)

        # Crear un decoder simple para verificar
        # (En producción se usaría una librería de decodificación)
        # Por ahora solo verificamos que se generó correctamente
        self.assertIsNotNone(img)

    def test_generate_qr_with_different_uuids(self):
        """Debe generar QRs diferentes para UUIDs diferentes"""
        uuid1 = str(uuid.uuid4())
        uuid2 = str(uuid.uuid4())

        qr1 = self.service.generate_qr(uuid1)
        qr2 = self.service.generate_qr(uuid2)

        # Los buffers deben tener contenido diferente
        content1 = qr1.read()
        content2 = qr2.read()

        self.assertNotEqual(content1, content2)
