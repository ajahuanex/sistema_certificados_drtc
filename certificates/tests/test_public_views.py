"""Tests para vistas públicas"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date
import uuid as uuid_lib

from certificates.models import (
    Event, Participant, Certificate, CertificateTemplate, AuditLog
)


class CertificateQueryViewTest(TestCase):
    """Tests para la vista de consulta por DNI"""

    def setUp(self):
        """Configuración inicial para los tests"""
        self.client = Client()
        
        # Crear plantilla por defecto
        self.template = CertificateTemplate.objects.create(
            name="Plantilla Test",
            html_template="<html><body>Test</body></html>",
            is_default=True
        )
        
        # Crear eventos
        self.event1 = Event.objects.create(
            name="Capacitación Django",
            event_date=date(2024, 1, 15),
            template=self.template
        )
        
        self.event2 = Event.objects.create(
            name="Capacitación Python",
            event_date=date(2024, 2, 20),
            template=self.template
        )
        
        # Crear participantes
        self.participant1 = Participant.objects.create(
            dni="12345678",
            full_name="Juan Pérez García",
            event=self.event1,
            attendee_type="ASISTENTE"
        )
        
        self.participant2 = Participant.objects.create(
            dni="12345678",
            full_name="Juan Pérez García",
            event=self.event2,
            attendee_type="PONENTE"
        )
        
        self.participant3 = Participant.objects.create(
            dni="87654321",
            full_name="María López Silva",
            event=self.event1,
            attendee_type="ORGANIZADOR"
        )
        
        # Crear certificados
        self.cert1 = Certificate.objects.create(
            participant=self.participant1,
            pdf_file=SimpleUploadedFile("cert1.pdf", b"PDF content 1"),
            qr_code=SimpleUploadedFile("qr1.png", b"QR content 1"),
            verification_url=f"http://testserver/verificar/{uuid_lib.uuid4()}/"
        )
        
        self.cert2 = Certificate.objects.create(
            participant=self.participant2,
            pdf_file=SimpleUploadedFile("cert2.pdf", b"PDF content 2"),
            qr_code=SimpleUploadedFile("qr2.png", b"QR content 2"),
            verification_url=f"http://testserver/verificar/{uuid_lib.uuid4()}/"
        )
        
        self.cert3 = Certificate.objects.create(
            participant=self.participant3,
            pdf_file=SimpleUploadedFile("cert3.pdf", b"PDF content 3"),
            qr_code=SimpleUploadedFile("qr3.png", b"QR content 3"),
            verification_url=f"http://testserver/verificar/{uuid_lib.uuid4()}/"
        )

    def test_get_shows_form(self):
        """Test que GET muestra el formulario de consulta"""
        response = self.client.get(reverse('certificates:query'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'certificates/query.html')
        self.assertIn('form', response.context)
        self.assertContains(response, 'DNI')

    def test_post_with_valid_dni_returns_certificates(self):
        """Test que POST con DNI válido retorna certificados"""
        response = self.client.post(
            reverse('certificates:query'),
            {'dni': '12345678'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('certificates', response.context)
        self.assertEqual(len(response.context['certificates']), 2)
        self.assertEqual(response.context['dni'], '12345678')

    def test_post_orders_by_event_date_descending(self):
        """Test que los resultados se ordenan por fecha descendente"""
        response = self.client.post(
            reverse('certificates:query'),
            {'dni': '12345678'}
        )
        
        certificates = list(response.context['certificates'])
        # El evento más reciente (event2) debe aparecer primero
        self.assertEqual(
            certificates[0].participant.event.event_date,
            date(2024, 2, 20)
        )
        self.assertEqual(
            certificates[1].participant.event.event_date,
            date(2024, 1, 15)
        )

    def test_post_with_no_results(self):
        """Test que POST con DNI sin certificados muestra lista vacía"""
        response = self.client.post(
            reverse('certificates:query'),
            {'dni': '99999999'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('certificates', response.context)
        self.assertEqual(len(response.context['certificates']), 0)

    def test_post_with_invalid_dni_shows_errors(self):
        """Test que POST con DNI inválido muestra errores"""
        response = self.client.post(
            reverse('certificates:query'),
            {'dni': '123'}  # DNI muy corto
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)
        self.assertIn('dni', response.context['form'].errors)

    def test_post_with_non_numeric_dni_shows_errors(self):
        """Test que POST con DNI no numérico muestra errores"""
        response = self.client.post(
            reverse('certificates:query'),
            {'dni': 'abcd1234'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_query_creates_audit_log(self):
        """Test que la consulta crea un registro de auditoría"""
        initial_count = AuditLog.objects.filter(action_type='QUERY').count()
        
        self.client.post(
            reverse('certificates:query'),
            {'dni': '12345678'}
        )
        
        final_count = AuditLog.objects.filter(action_type='QUERY').count()
        self.assertEqual(final_count, initial_count + 1)
        
        # Verificar contenido del log
        log = AuditLog.objects.filter(action_type='QUERY').latest('timestamp')
        self.assertEqual(log.metadata['dni'], '12345678')
        self.assertEqual(log.metadata['results_count'], 2)
        self.assertIsNotNone(log.ip_address)

    def test_query_uses_select_related(self):
        """Test que la consulta usa select_related para optimizar queries"""
        with self.assertNumQueries(2):  # 1 para certificados + 1 para audit log
            response = self.client.post(
                reverse('certificates:query'),
                {'dni': '12345678'}
            )
            # Acceder a datos relacionados no debe generar queries adicionales
            certificates = response.context['certificates']
            for cert in certificates:
                _ = cert.participant.full_name
                _ = cert.participant.event.name


class CertificateDownloadViewTest(TestCase):
    """Tests para la vista de descarga de certificados"""

    def setUp(self):
        """Configuración inicial para los tests"""
        self.client = Client()
        
        # Crear plantilla
        self.template = CertificateTemplate.objects.create(
            name="Plantilla Test",
            html_template="<html><body>Test</body></html>",
            is_default=True
        )
        
        # Crear evento y participante
        self.event = Event.objects.create(
            name="Capacitación Test",
            event_date=date(2024, 1, 15),
            template=self.template
        )
        
        self.participant = Participant.objects.create(
            dni="12345678",
            full_name="Juan Pérez",
            event=self.event,
            attendee_type="ASISTENTE"
        )
        
        # Crear certificado con archivo PDF
        self.certificate = Certificate.objects.create(
            participant=self.participant,
            pdf_file=SimpleUploadedFile("test.pdf", b"PDF content"),
            qr_code=SimpleUploadedFile("qr.png", b"QR content"),
            verification_url="http://testserver/verificar/test/"
        )

    def test_download_returns_pdf_file(self):
        """Test que la descarga retorna el archivo PDF"""
        response = self.client.get(
            reverse('certificates:download', kwargs={'uuid': self.certificate.uuid})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_download_sets_content_disposition_header(self):
        """Test que se configura el header Content-Disposition"""
        response = self.client.get(
            reverse('certificates:download', kwargs={'uuid': self.certificate.uuid})
        )
        
        self.assertIn('Content-Disposition', response)
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn(str(self.certificate.uuid), response['Content-Disposition'])
        self.assertIn(self.participant.dni, response['Content-Disposition'])

    def test_download_with_invalid_uuid_returns_404(self):
        """Test que UUID inválido retorna 404"""
        invalid_uuid = uuid_lib.uuid4()
        response = self.client.get(
            reverse('certificates:download', kwargs={'uuid': invalid_uuid})
        )
        
        self.assertEqual(response.status_code, 404)

    def test_download_without_pdf_file_returns_404(self):
        """Test que certificado sin PDF retorna 404"""
        # Crear certificado sin archivo PDF
        participant2 = Participant.objects.create(
            dni="87654321",
            full_name="María López",
            event=self.event,
            attendee_type="PONENTE"
        )
        
        cert_without_pdf = Certificate.objects.create(
            participant=participant2,
            pdf_file='',  # Sin archivo
            qr_code=SimpleUploadedFile("qr2.png", b"QR content"),
            verification_url="http://testserver/verificar/test2/"
        )
        
        response = self.client.get(
            reverse('certificates:download', kwargs={'uuid': cert_without_pdf.uuid})
        )
        
        self.assertEqual(response.status_code, 404)


class CertificateVerificationViewTest(TestCase):
    """Tests para la vista de verificación por QR"""

    def setUp(self):
        """Configuración inicial para los tests"""
        self.client = Client()
        
        # Crear plantilla
        self.template = CertificateTemplate.objects.create(
            name="Plantilla Test",
            html_template="<html><body>Test</body></html>",
            is_default=True
        )
        
        # Crear evento y participante
        self.event = Event.objects.create(
            name="Capacitación Django Avanzado",
            event_date=date(2024, 1, 15),
            template=self.template
        )
        
        self.participant = Participant.objects.create(
            dni="12345678",
            full_name="Juan Pérez García",
            event=self.event,
            attendee_type="ASISTENTE"
        )
        
        # Crear certificado sin firma
        self.certificate = Certificate.objects.create(
            participant=self.participant,
            pdf_file=SimpleUploadedFile("test.pdf", b"PDF content"),
            qr_code=SimpleUploadedFile("qr.png", b"QR content"),
            verification_url="http://testserver/verificar/test/",
            is_signed=False
        )
        
        # Crear certificado firmado
        self.participant_signed = Participant.objects.create(
            dni="87654321",
            full_name="María López Silva",
            event=self.event,
            attendee_type="PONENTE"
        )
        
        self.certificate_signed = Certificate.objects.create(
            participant=self.participant_signed,
            pdf_file=SimpleUploadedFile("test2.pdf", b"PDF content 2"),
            qr_code=SimpleUploadedFile("qr2.png", b"QR content 2"),
            verification_url="http://testserver/verificar/test2/",
            is_signed=True
        )

    def test_verify_shows_certificate_details(self):
        """Test que la verificación muestra los datos del certificado"""
        response = self.client.get(
            reverse('certificates:verify', kwargs={'uuid': self.certificate.uuid})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'certificates/verify.html')
        self.assertEqual(response.context['certificate'], self.certificate)
        
        # Verificar que se muestran los datos
        self.assertContains(response, self.participant.dni)
        self.assertContains(response, self.participant.full_name)
        self.assertContains(response, self.event.name)
        self.assertContains(response, self.participant.get_attendee_type_display())

    def test_verify_shows_signature_status(self):
        """Test que muestra el estado de firma digital"""
        # Certificado sin firmar
        response = self.client.get(
            reverse('certificates:verify', kwargs={'uuid': self.certificate.uuid})
        )
        self.assertContains(response, 'SIN FIRMA DIGITAL')
        
        # Certificado firmado
        response = self.client.get(
            reverse('certificates:verify', kwargs={'uuid': self.certificate_signed.uuid})
        )
        self.assertContains(response, 'FIRMADO DIGITALMENTE')

    def test_verify_with_invalid_uuid_returns_404(self):
        """Test que UUID inválido retorna 404"""
        invalid_uuid = uuid_lib.uuid4()
        response = self.client.get(
            reverse('certificates:verify', kwargs={'uuid': invalid_uuid})
        )
        
        self.assertEqual(response.status_code, 404)

    def test_verify_creates_audit_log(self):
        """Test que la verificación crea un registro de auditoría"""
        initial_count = AuditLog.objects.filter(action_type='VERIFY').count()
        
        self.client.get(
            reverse('certificates:verify', kwargs={'uuid': self.certificate.uuid})
        )
        
        final_count = AuditLog.objects.filter(action_type='VERIFY').count()
        self.assertEqual(final_count, initial_count + 1)
        
        # Verificar contenido del log
        log = AuditLog.objects.filter(action_type='VERIFY').latest('timestamp')
        self.assertEqual(log.metadata['certificate_uuid'], str(self.certificate.uuid))
        self.assertEqual(log.metadata['participant_dni'], self.participant.dni)
        self.assertEqual(log.metadata['participant_name'], self.participant.full_name)
        self.assertEqual(log.metadata['event_name'], self.event.name)
        self.assertEqual(log.metadata['is_signed'], False)
        self.assertIsNotNone(log.ip_address)

    def test_verify_invalid_certificate_creates_audit_log(self):
        """Test que intento de verificación fallido crea log"""
        invalid_uuid = uuid_lib.uuid4()
        initial_count = AuditLog.objects.filter(action_type='VERIFY').count()
        
        response = self.client.get(
            reverse('certificates:verify', kwargs={'uuid': invalid_uuid})
        )
        
        self.assertEqual(response.status_code, 404)
        
        final_count = AuditLog.objects.filter(action_type='VERIFY').count()
        self.assertEqual(final_count, initial_count + 1)
        
        # Verificar contenido del log
        log = AuditLog.objects.filter(action_type='VERIFY').latest('timestamp')
        self.assertEqual(log.metadata['certificate_uuid'], str(invalid_uuid))
        self.assertEqual(log.metadata['status'], 'not_found')

    def test_verify_uses_select_related(self):
        """Test que la verificación usa select_related para optimizar queries"""
        with self.assertNumQueries(2):  # 1 para certificado + 1 para audit log
            response = self.client.get(
                reverse('certificates:verify', kwargs={'uuid': self.certificate.uuid})
            )
            # Acceder a datos relacionados no debe generar queries adicionales
            cert = response.context['certificate']
            _ = cert.participant.full_name
            _ = cert.participant.event.name

