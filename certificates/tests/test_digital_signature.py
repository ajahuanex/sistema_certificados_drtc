"""Tests para DigitalSignatureService"""
from django.test import TestCase, override_settings
from unittest.mock import Mock, patch, MagicMock
from certificates.services.digital_signature import DigitalSignatureService
from certificates.models import Event, Participant, Certificate, CertificateTemplate
from datetime import date
from io import BytesIO
import requests


class DigitalSignatureServiceTest(TestCase):
    """Tests para el servicio de firma digital"""

    def setUp(self):
        self.service = DigitalSignatureService()

        # Crear datos de prueba
        self.template = CertificateTemplate.objects.create(
            name="Plantilla Test", html_template="<html></html>", is_default=True
        )

        self.event = Event.objects.create(
            name="Evento Test", event_date=date(2024, 1, 1)
        )

        self.participant = Participant.objects.create(
            dni="12345678",
            full_name="Juan Pérez",
            event=self.event,
            attendee_type="ASISTENTE",
        )

        # Crear certificado de prueba
        self.certificate = Certificate.objects.create(
            participant=self.participant, verification_url="http://test.com/verify/123"
        )

        # Crear archivo PDF de prueba
        pdf_content = b"%PDF-1.4 test content"
        self.certificate.pdf_file.save("test.pdf", BytesIO(pdf_content), save=True)

    @override_settings(
        SIGNATURE_SERVICE_URL="http://test-signature.com/sign",
        SIGNATURE_API_KEY="test-api-key",
    )
    @patch("certificates.services.digital_signature.requests.post")
    def test_send_to_signature_service_success(self, mock_post):
        """Debe enviar PDF al servicio y recibir PDF firmado"""
        # Reinicializar servicio con nuevos settings
        service = DigitalSignatureService()

        # Mock de respuesta exitosa
        signed_pdf = b"%PDF-1.4 signed content"
        mock_response = Mock()
        mock_response.content = signed_pdf
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Enviar PDF
        result = service._send_to_signature_service(self.certificate.pdf_file)

        # Verificar que se llamó al servicio correctamente
        mock_post.assert_called_once()
        call_args = mock_post.call_args

        self.assertEqual(call_args[0][0], "http://test-signature.com/sign")
        self.assertIn("Authorization", call_args[1]["headers"])
        self.assertEqual(
            call_args[1]["headers"]["Authorization"], "Bearer test-api-key"
        )
        self.assertEqual(call_args[1]["timeout"], 30)

        # Verificar resultado
        self.assertEqual(result, signed_pdf)

    @patch("certificates.services.digital_signature.requests.post")
    def test_send_to_signature_service_http_error(self, mock_post):
        """Debe manejar errores HTTP del servicio"""
        # Mock de respuesta con error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "500 Server Error"
        )
        mock_post.return_value = mock_response

        # Debe lanzar excepción
        with self.assertRaises(requests.exceptions.HTTPError):
            self.service._send_to_signature_service(self.certificate.pdf_file)

    @patch("certificates.services.digital_signature.requests.post")
    def test_send_to_signature_service_timeout(self, mock_post):
        """Debe manejar timeout del servicio"""
        # Mock de timeout
        mock_post.side_effect = requests.exceptions.Timeout("Connection timeout")

        # Debe lanzar excepción
        with self.assertRaises(requests.exceptions.Timeout):
            self.service._send_to_signature_service(self.certificate.pdf_file)

    @patch("certificates.services.digital_signature.requests.post")
    def test_send_to_signature_service_connection_error(self, mock_post):
        """Debe manejar errores de conexión"""
        # Mock de error de conexión
        mock_post.side_effect = requests.exceptions.ConnectionError(
            "Connection refused"
        )

        # Debe lanzar excepción
        with self.assertRaises(requests.exceptions.ConnectionError):
            self.service._send_to_signature_service(self.certificate.pdf_file)


    @patch("certificates.services.digital_signature.requests.post")
    @patch("certificates.services.digital_signature.time.sleep")
    def test_sign_certificate_success_on_first_try(self, mock_sleep, mock_post):
        """Debe firmar certificado exitosamente en el primer intento"""
        # Mock de respuesta exitosa
        signed_pdf = b"%PDF-1.4 signed content"
        mock_response = Mock()
        mock_response.content = signed_pdf
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Mock del método _update_certificate_status
        with patch.object(
            self.service, "_update_certificate_status"
        ) as mock_update:
            result = self.service.sign_certificate(self.certificate)

            # Verificar que se llamó al servicio una sola vez
            self.assertEqual(mock_post.call_count, 1)

            # Verificar que no se durmió (no hubo reintentos)
            mock_sleep.assert_not_called()

            # Verificar que se actualizó el certificado
            mock_update.assert_called_once()

    @patch("certificates.services.digital_signature.requests.post")
    @patch("certificates.services.digital_signature.time.sleep")
    def test_sign_certificate_retries_on_timeout(self, mock_sleep, mock_post):
        """Debe reintentar cuando hay timeout"""
        # Primer intento: timeout, segundo intento: éxito
        signed_pdf = b"%PDF-1.4 signed content"
        mock_response = Mock()
        mock_response.content = signed_pdf
        mock_response.raise_for_status = Mock()

        mock_post.side_effect = [
            requests.exceptions.Timeout("Timeout"),
            mock_response,
        ]

        with patch.object(self.service, "_update_certificate_status"):
            result = self.service.sign_certificate(self.certificate)

            # Verificar que se intentó 2 veces
            self.assertEqual(mock_post.call_count, 2)

            # Verificar que se durmió 1 vez (entre intentos)
            mock_sleep.assert_called_once_with(2)

    @patch("certificates.services.digital_signature.requests.post")
    @patch("certificates.services.digital_signature.time.sleep")
    def test_sign_certificate_fails_after_max_retries(self, mock_sleep, mock_post):
        """Debe fallar después de MAX_RETRIES intentos"""
        # Todos los intentos fallan
        mock_post.side_effect = requests.exceptions.Timeout("Timeout")

        with self.assertRaises(Exception) as context:
            self.service.sign_certificate(self.certificate)

        # Verificar que se intentó MAX_RETRIES veces
        self.assertEqual(mock_post.call_count, 3)

        # Verificar que se durmió MAX_RETRIES-1 veces
        self.assertEqual(mock_sleep.call_count, 2)

        # Verificar mensaje de error
        self.assertIn("después de 3 intentos", str(context.exception))

    def test_sign_certificate_skips_already_signed(self):
        """No debe firmar certificados ya firmados"""
        # Marcar certificado como firmado
        self.certificate.is_signed = True
        self.certificate.save()

        with patch.object(self.service, "_send_to_signature_service") as mock_send:
            result = self.service.sign_certificate(self.certificate)

            # Verificar que no se llamó al servicio
            mock_send.assert_not_called()

            # Debe retornar el mismo certificado
            self.assertEqual(result.id, self.certificate.id)


    def test_update_certificate_status(self):
        """Debe actualizar el estado del certificado correctamente"""
        from certificates.models import AuditLog

        # Estado inicial
        self.assertFalse(self.certificate.is_signed)
        self.assertIsNone(self.certificate.signed_at)

        signed_pdf = b"%PDF-1.4 signed content"
        initial_audit_count = AuditLog.objects.count()

        # Actualizar estado
        self.service._update_certificate_status(self.certificate, signed_pdf)

        # Recargar certificado
        self.certificate.refresh_from_db()

        # Verificar cambios
        self.assertTrue(self.certificate.is_signed)
        self.assertIsNotNone(self.certificate.signed_at)

        # Verificar que se creó registro de auditoría
        self.assertEqual(AuditLog.objects.count(), initial_audit_count + 1)

        log = AuditLog.objects.latest("timestamp")
        self.assertEqual(log.action_type, "SIGN")
        self.assertIn(self.participant.dni, log.metadata["participant_dni"])

    def test_update_certificate_status_replaces_pdf(self):
        """Debe reemplazar el PDF con la versión firmada"""
        signed_pdf = b"%PDF-1.4 signed content with signature"

        # PDF original
        original_size = self.certificate.pdf_file.size

        # Actualizar
        self.service._update_certificate_status(self.certificate, signed_pdf)

        # Recargar
        self.certificate.refresh_from_db()

        # Verificar que el PDF cambió
        self.certificate.pdf_file.seek(0)
        new_content = self.certificate.pdf_file.read()
        self.assertEqual(new_content, signed_pdf)


    @patch("certificates.services.digital_signature.requests.post")
    def test_sign_bulk_certificates_success(self, mock_post):
        """Debe firmar múltiples certificados exitosamente"""
        # Crear más certificados
        participant2 = Participant.objects.create(
            dni="87654321",
            full_name="María López",
            event=self.event,
            attendee_type="PONENTE",
        )

        cert2 = Certificate.objects.create(
            participant=participant2, verification_url="http://test.com/verify/456"
        )
        cert2.pdf_file.save("test2.pdf", BytesIO(b"%PDF-1.4 test"), save=True)

        # Mock de respuesta exitosa
        signed_pdf = b"%PDF-1.4 signed content"
        mock_response = Mock()
        mock_response.content = signed_pdf
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Firmar en masa
        certificates = [self.certificate, cert2]
        result = self.service.sign_bulk_certificates(certificates)

        # Verificar resultados
        self.assertEqual(result["success_count"], 2)
        self.assertEqual(result["error_count"], 0)
        self.assertEqual(len(result["errors"]), 0)

    @patch("certificates.services.digital_signature.requests.post")
    def test_sign_bulk_certificates_with_errors(self, mock_post):
        """Debe manejar errores individuales sin detener el proceso"""
        # Crear más certificados
        participant2 = Participant.objects.create(
            dni="87654321",
            full_name="María López",
            event=self.event,
            attendee_type="PONENTE",
        )

        cert2 = Certificate.objects.create(
            participant=participant2, verification_url="http://test.com/verify/456"
        )
        cert2.pdf_file.save("test2.pdf", BytesIO(b"%PDF-1.4 test"), save=True)

        # Primer certificado falla, segundo tiene éxito
        signed_pdf = b"%PDF-1.4 signed content"
        mock_response = Mock()
        mock_response.content = signed_pdf
        mock_response.raise_for_status = Mock()

        mock_post.side_effect = [
            requests.exceptions.Timeout("Timeout"),
            requests.exceptions.Timeout("Timeout"),
            requests.exceptions.Timeout("Timeout"),
            mock_response,
        ]

        certificates = [self.certificate, cert2]
        result = self.service.sign_bulk_certificates(certificates)

        # Verificar que procesó ambos
        self.assertEqual(result["success_count"], 1)
        self.assertEqual(result["error_count"], 1)
        self.assertGreater(len(result["errors"]), 0)

    def test_sign_bulk_certificates_skips_already_signed(self):
        """Debe omitir certificados ya firmados"""
        # Marcar certificado como firmado
        self.certificate.is_signed = True
        self.certificate.save()

        with patch.object(self.service, "sign_certificate") as mock_sign:
            result = self.service.sign_bulk_certificates([self.certificate])

            # No debe intentar firmar
            mock_sign.assert_not_called()

            # Resultado debe indicar que no hay certificados sin firmar
            self.assertEqual(result["success_count"], 0)
            self.assertEqual(result["error_count"], 0)

    def test_sign_bulk_certificates_with_empty_list(self):
        """Debe manejar lista vacía de certificados"""
        result = self.service.sign_bulk_certificates([])

        self.assertEqual(result["success_count"], 0)
        self.assertEqual(result["error_count"], 0)
