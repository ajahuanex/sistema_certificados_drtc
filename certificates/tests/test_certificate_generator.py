"""Tests para CertificateGeneratorService"""
from django.test import TestCase
from certificates.services.certificate_generator import CertificateGeneratorService
from certificates.models import Event, Participant, CertificateTemplate
from datetime import date


class CertificateGeneratorServiceTest(TestCase):
    """Tests para el servicio de generación de certificados"""

    def setUp(self):
        self.service = CertificateGeneratorService()

        # Crear plantilla por defecto
        self.template = CertificateTemplate.objects.create(
            name="Plantilla por defecto",
            html_template="""
            <html>
            <body>
                <h1>Certificado</h1>
                <p>Nombre: {{ full_name }}</p>
                <p>DNI: {{ dni }}</p>
                <p>Evento: {{ event_name }}</p>
                <p>Fecha: {{ event_date }}</p>
                <p>Tipo: {{ attendee_type }}</p>
            </body>
            </html>
            """,
            is_default=True,
        )

        # Crear evento
        self.event = Event.objects.create(
            name="Capacitación Django", event_date=date(2024, 1, 1)
        )

        # Crear participante
        self.participant = Participant.objects.create(
            dni="12345678",
            full_name="Juan Pérez",
            event=self.event,
            attendee_type="ASISTENTE",
        )

    def test_render_template_with_valid_data(self):
        """Debe renderizar correctamente una plantilla con datos válidos"""
        context_data = {
            "full_name": "Juan Pérez",
            "dni": "12345678",
            "event_name": "Capacitación Django",
            "event_date": "01/01/2024",
            "attendee_type": "ASISTENTE",
        }

        rendered = self.service._render_template(
            self.template.html_template, context_data
        )

        self.assertIn("Juan Pérez", rendered)
        self.assertIn("12345678", rendered)
        self.assertIn("Capacitación Django", rendered)
        self.assertIn("01/01/2024", rendered)
        self.assertIn("ASISTENTE", rendered)

    def test_render_template_with_empty_context(self):
        """Debe renderizar plantilla incluso con contexto vacío"""
        rendered = self.service._render_template(self.template.html_template, {})

        self.assertIn("<h1>Certificado</h1>", rendered)

    def test_get_template_uses_event_template(self):
        """Debe usar la plantilla del evento si existe"""
        # Crear plantilla específica para el evento
        event_template = CertificateTemplate.objects.create(
            name="Plantilla del evento",
            html_template="<html><body>Plantilla específica</body></html>",
            is_default=False,
        )

        self.event.template = event_template
        self.event.save()

        template = self.service._get_template(self.participant)

        self.assertEqual(template.id, event_template.id)

    def test_get_template_uses_default_when_no_event_template(self):
        """Debe usar plantilla por defecto si el evento no tiene plantilla"""
        template = self.service._get_template(self.participant)

        self.assertEqual(template.id, self.template.id)
        self.assertTrue(template.is_default)

    def test_get_template_raises_error_when_no_default(self):
        """Debe lanzar error si no hay plantilla por defecto"""
        # Eliminar plantilla por defecto
        CertificateTemplate.objects.all().delete()

        with self.assertRaises(ValueError) as context:
            self.service._get_template(self.participant)

        self.assertIn("No hay plantilla por defecto", str(context.exception))


    def test_create_pdf_with_participant_data(self):
        """Debe generar un PDF con datos del participante"""
        context_data = {
            "full_name": "Juan Pérez",
            "dni": "12345678",
            "event_name": "Capacitación Django",
            "event_date": "01/01/2024",
            "attendee_type": "ASISTENTE",
        }

        pdf_bytes = self.service._create_pdf(context_data, self.template)

        self.assertIsNotNone(pdf_bytes)
        self.assertGreater(len(pdf_bytes), 0)
        # Verificar que es un PDF válido (comienza con %PDF)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_create_pdf_with_qr_code(self):
        """Debe generar PDF con código QR embebido"""
        from io import BytesIO
        from PIL import Image

        # Crear una imagen QR de prueba
        qr_buffer = BytesIO()
        img = Image.new("RGB", (300, 300), color="white")
        img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        context_data = {
            "full_name": "Juan Pérez",
            "dni": "12345678",
            "event_name": "Capacitación Django",
            "event_date": "01/01/2024",
            "attendee_type": "PONENTE",
        }

        pdf_bytes = self.service._create_pdf(
            context_data, self.template, qr_buffer=qr_buffer
        )

        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        # El PDF debe ser más grande porque incluye la imagen
        self.assertGreater(len(pdf_bytes), 1000)


    def test_generate_certificate_creates_certificate(self):
        """Debe crear un certificado completo"""
        from certificates.models import Certificate

        certificate = self.service.generate_certificate(self.participant)

        self.assertIsNotNone(certificate)
        self.assertEqual(certificate.participant, self.participant)
        self.assertIsNotNone(certificate.uuid)
        self.assertIsNotNone(certificate.pdf_file)
        self.assertIsNotNone(certificate.qr_code)
        self.assertIsNotNone(certificate.verification_url)
        self.assertFalse(certificate.is_signed)

    def test_generate_certificate_creates_audit_log(self):
        """Debe crear un registro de auditoría"""
        from certificates.models import AuditLog

        initial_count = AuditLog.objects.count()

        self.service.generate_certificate(self.participant)

        self.assertEqual(AuditLog.objects.count(), initial_count + 1)

        log = AuditLog.objects.latest("timestamp")
        self.assertEqual(log.action_type, "GENERATE")
        self.assertIn(self.participant.dni, log.metadata["participant_dni"])

    def test_generate_certificate_does_not_duplicate(self):
        """No debe crear certificados duplicados"""
        from certificates.models import Certificate

        # Generar primer certificado
        cert1 = self.service.generate_certificate(self.participant)

        # Intentar generar otro
        cert2 = self.service.generate_certificate(self.participant)

        # Debe retornar el mismo certificado
        self.assertEqual(cert1.id, cert2.id)
        self.assertEqual(Certificate.objects.filter(participant=self.participant).count(), 1)

    def test_generate_certificate_with_user(self):
        """Debe registrar el usuario en auditoría"""
        from django.contrib.auth.models import User
        from certificates.models import AuditLog

        user = User.objects.create_user(username="admin", password="test123")

        self.service.generate_certificate(self.participant, user=user)

        log = AuditLog.objects.latest("timestamp")
        self.assertEqual(log.user, user)


    def test_generate_bulk_certificates_for_event(self):
        """Debe generar certificados para todos los participantes de un evento"""
        # Crear más participantes
        Participant.objects.create(
            dni="87654321",
            full_name="María López",
            event=self.event,
            attendee_type="PONENTE",
        )

        Participant.objects.create(
            dni="11223344",
            full_name="Carlos Ruiz",
            event=self.event,
            attendee_type="ORGANIZADOR",
        )

        result = self.service.generate_bulk_certificates(self.event)

        self.assertEqual(result["success_count"], 3)
        self.assertEqual(result["error_count"], 0)
        self.assertEqual(len(result["certificates"]), 3)
        self.assertEqual(len(result["errors"]), 0)

    def test_generate_bulk_certificates_with_no_participants(self):
        """Debe manejar eventos sin participantes"""
        # Crear evento sin participantes
        empty_event = Event.objects.create(
            name="Evento Vacío", event_date=date(2024, 2, 1)
        )

        result = self.service.generate_bulk_certificates(empty_event)

        self.assertEqual(result["success_count"], 0)
        self.assertEqual(result["error_count"], 0)
        self.assertEqual(len(result["certificates"]), 0)
        self.assertGreater(len(result["errors"]), 0)

    def test_generate_bulk_certificates_handles_errors(self):
        """Debe manejar errores individuales sin detener el proceso"""
        # Crear participantes
        Participant.objects.create(
            dni="87654321",
            full_name="María López",
            event=self.event,
            attendee_type="PONENTE",
        )

        # Generar certificados (el primero ya existe del setUp)
        result = self.service.generate_bulk_certificates(self.event)

        # Debe procesar todos aunque algunos ya existan
        self.assertGreaterEqual(result["success_count"], 1)
