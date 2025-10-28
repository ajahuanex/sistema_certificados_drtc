"""Tests para Django Admin"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from certificates.models import (
    Event,
    Participant,
    Certificate,
    CertificateTemplate,
    AuditLog,
)
from datetime import date


class AdminTest(TestCase):
    """Tests para la configuración del admin"""

    def setUp(self):
        # Crear superusuario
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="admin123"
        )

        self.client = Client()
        self.client.login(username="admin", password="admin123")

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

    def test_event_admin_accessible(self):
        """Debe poder acceder al admin de eventos"""
        url = reverse("admin:certificates_event_changelist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Evento Test")

    def test_participant_admin_accessible(self):
        """Debe poder acceder al admin de participantes"""
        url = reverse("admin:certificates_participant_changelist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Juan Pérez")

    def test_certificate_admin_accessible(self):
        """Debe poder acceder al admin de certificados"""
        url = reverse("admin:certificates_certificate_changelist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_template_admin_accessible(self):
        """Debe poder acceder al admin de plantillas"""
        url = reverse("admin:certificates_certificatetemplate_changelist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Plantilla Test")

    def test_auditlog_admin_accessible(self):
        """Debe poder acceder al admin de auditoría"""
        url = reverse("admin:certificates_auditlog_changelist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_auditlog_admin_readonly(self):
        """El admin de auditoría debe ser solo lectura"""
        # Crear un log
        log = AuditLog.objects.create(
            action_type="IMPORT", description="Test log", metadata={}
        )

        # Intentar acceder a la página de edición
        url = reverse("admin:certificates_auditlog_change", args=[log.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        # Verificar que todos los campos son readonly
        self.assertContains(response, 'class="readonly"')

    def test_auditlog_admin_no_add_permission(self):
        """No debe permitir agregar registros de auditoría"""
        url = reverse("admin:certificates_auditlog_add")
        response = self.client.get(url)

        # Debe redirigir o dar 403
        self.assertIn(response.status_code, [302, 403])

    def test_auditlog_admin_no_delete_permission(self):
        """No debe permitir eliminar registros de auditoría"""
        log = AuditLog.objects.create(
            action_type="IMPORT", description="Test log", metadata={}
        )

        url = reverse("admin:certificates_auditlog_delete", args=[log.id])
        response = self.client.get(url)

        # Debe redirigir o dar 403
        self.assertIn(response.status_code, [302, 403])

    def test_event_admin_search(self):
        """Debe poder buscar eventos"""
        url = reverse("admin:certificates_event_changelist")
        response = self.client.get(url, {"q": "Evento Test"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Evento Test")

    def test_participant_admin_filter(self):
        """Debe poder filtrar participantes por tipo"""
        url = reverse("admin:certificates_participant_changelist")
        response = self.client.get(url, {"attendee_type": "ASISTENTE"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Juan Pérez")



class AdminActionsTest(TestCase):
    """Tests para acciones admin personalizadas"""

    def setUp(self):
        # Crear superusuario
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="admin123"
        )

        self.client = Client()
        self.client.login(username="admin", password="admin123")

        # Crear datos de prueba
        self.template = CertificateTemplate.objects.create(
            name="Plantilla Test", html_template="<html></html>", is_default=True
        )

        self.event = Event.objects.create(
            name="Evento Test", event_date=date(2024, 1, 1)
        )

        self.participant1 = Participant.objects.create(
            dni="12345678",
            full_name="Juan Pérez",
            event=self.event,
            attendee_type="ASISTENTE",
        )

        self.participant2 = Participant.objects.create(
            dni="87654321",
            full_name="María López",
            event=self.event,
            attendee_type="PONENTE",
        )

    def test_generate_certificates_action(self):
        """Debe generar certificados para un evento"""
        from certificates.admin import EventAdmin
        from django.contrib.admin.sites import AdminSite
        from unittest.mock import Mock

        # Crear instancia del admin
        site = AdminSite()
        event_admin = EventAdmin(Event, site)

        # Mock del request
        request = Mock()
        request.user = self.admin_user

        # Ejecutar acción
        queryset = Event.objects.filter(id=self.event.id)
        event_admin.generate_certificates_action(request, queryset)

        # Verificar que se generaron certificados
        self.assertEqual(Certificate.objects.count(), 2)

    def test_download_pdf_action_single(self):
        """Debe descargar un solo PDF"""
        from certificates.admin import CertificateAdmin
        from certificates.services.certificate_generator import (
            CertificateGeneratorService,
        )
        from django.contrib.admin.sites import AdminSite
        from unittest.mock import Mock

        # Generar certificado
        service = CertificateGeneratorService()
        cert = service.generate_certificate(self.participant1)

        # Crear instancia del admin
        site = AdminSite()
        cert_admin = CertificateAdmin(Certificate, site)

        # Mock del request
        request = Mock()
        request.user = self.admin_user

        # Ejecutar acción
        queryset = Certificate.objects.filter(id=cert.id)
        response = cert_admin.download_pdf_action(request, queryset)

        # Verificar respuesta
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment", response["Content-Disposition"])

    def test_download_pdf_action_multiple(self):
        """Debe descargar múltiples PDFs como ZIP"""
        from certificates.admin import CertificateAdmin
        from certificates.services.certificate_generator import (
            CertificateGeneratorService,
        )
        from django.contrib.admin.sites import AdminSite
        from unittest.mock import Mock

        # Generar certificados
        service = CertificateGeneratorService()
        cert1 = service.generate_certificate(self.participant1)
        cert2 = service.generate_certificate(self.participant2)

        # Crear instancia del admin
        site = AdminSite()
        cert_admin = CertificateAdmin(Certificate, site)

        # Mock del request
        request = Mock()
        request.user = self.admin_user

        # Ejecutar acción
        queryset = Certificate.objects.all()
        response = cert_admin.download_pdf_action(request, queryset)

        # Verificar respuesta
        self.assertEqual(response["Content-Type"], "application/zip")
        self.assertIn("certificados.zip", response["Content-Disposition"])
