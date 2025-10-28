"""Tests para las URLs de la aplicación certificates"""
from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from certificates.views.admin_views import ExcelImportView
from certificates.views.public_views import (
    CertificateQueryView,
    CertificateDownloadView,
    CertificateVerificationView,
)
from certificates.models import Event, Participant, Certificate
from datetime import date
import uuid

User = get_user_model()


class URLResolutionTest(TestCase):
    """Tests para verificar que las URLs resuelven correctamente"""

    def test_import_excel_url_resolves(self):
        """Verifica que la URL de importación Excel resuelve correctamente"""
        url = reverse('certificates:import_excel')
        self.assertEqual(url, '/admin/import-excel/')
        # La vista está decorada, así que verificamos el nombre de la función
        resolved = resolve(url)
        self.assertTrue(hasattr(resolved.func, 'view_class') or 'ExcelImportView' in str(resolved.func))

    def test_query_url_resolves(self):
        """Verifica que la URL de consulta resuelve correctamente"""
        url = reverse('certificates:query')
        self.assertEqual(url, '/consulta/')
        self.assertEqual(resolve(url).func.view_class, CertificateQueryView)

    def test_download_url_resolves(self):
        """Verifica que la URL de descarga resuelve correctamente"""
        test_uuid = uuid.uuid4()
        url = reverse('certificates:download', kwargs={'uuid': test_uuid})
        self.assertEqual(url, f'/certificado/{test_uuid}/descargar/')
        self.assertEqual(resolve(url).func.view_class, CertificateDownloadView)

    def test_verify_url_resolves(self):
        """Verifica que la URL de verificación resuelve correctamente"""
        test_uuid = uuid.uuid4()
        url = reverse('certificates:verify', kwargs={'uuid': test_uuid})
        self.assertEqual(url, f'/verificar/{test_uuid}/')
        self.assertEqual(resolve(url).func.view_class, CertificateVerificationView)


class URLAccessTest(TestCase):
    """Tests para verificar el acceso a las URLs"""

    def setUp(self):
        """Configuración inicial para los tests"""
        # Crear usuario staff para tests de admin
        self.staff_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_staff=True
        )
        
        # Crear usuario normal
        self.normal_user = User.objects.create_user(
            username='user',
            password='testpass123'
        )
        
        # Crear datos de prueba
        self.event = Event.objects.create(
            name='Evento de Prueba',
            event_date=date(2024, 1, 15),
            description='Descripción del evento'
        )
        
        self.participant = Participant.objects.create(
            dni='12345678',
            full_name='Juan Pérez',
            event=self.event,
            attendee_type='ASISTENTE'
        )
        
        self.certificate = Certificate.objects.create(
            participant=self.participant,
            verification_url=f'http://testserver/verificar/{uuid.uuid4()}/'
        )

    def test_import_excel_requires_staff(self):
        """Verifica que la importación Excel requiere usuario staff"""
        url = reverse('certificates:import_excel')
        
        # Sin autenticación - debe redirigir a login
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)
        
        # Con usuario normal - debe redirigir a login
        self.client.login(username='user', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)
        
        # Con usuario staff - debe permitir acceso
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_query_url_is_public(self):
        """Verifica que la URL de consulta es pública"""
        url = reverse('certificates:query')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'certificates/query.html')

    def test_download_url_is_public(self):
        """Verifica que la URL de descarga es pública"""
        url = reverse('certificates:download', kwargs={'uuid': self.certificate.uuid})
        response = self.client.get(url)
        # Debería retornar 404 porque no hay archivo PDF asociado
        self.assertEqual(response.status_code, 404)

    def test_verify_url_is_public(self):
        """Verifica que la URL de verificación es pública"""
        url = reverse('certificates:verify', kwargs={'uuid': self.certificate.uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'certificates/verify.html')

    def test_verify_url_with_invalid_uuid(self):
        """Verifica que la URL de verificación con UUID inválido retorna 404"""
        invalid_uuid = uuid.uuid4()
        url = reverse('certificates:verify', kwargs={'uuid': invalid_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class URLParametersTest(TestCase):
    """Tests para verificar que los parámetros de URL funcionan correctamente"""

    def setUp(self):
        """Configuración inicial"""
        self.event = Event.objects.create(
            name='Evento Test',
            event_date=date(2024, 1, 15)
        )
        
        self.participant = Participant.objects.create(
            dni='87654321',
            full_name='María García',
            event=self.event,
            attendee_type='PONENTE'
        )
        
        self.certificate = Certificate.objects.create(
            participant=self.participant,
            verification_url=f'http://testserver/verificar/{uuid.uuid4()}/'
        )

    def test_download_url_with_valid_uuid(self):
        """Verifica que la URL de descarga acepta UUID válido"""
        url = reverse('certificates:download', kwargs={'uuid': self.certificate.uuid})
        self.assertIn(str(self.certificate.uuid), url)
        
        # Verificar que la URL es accesible
        response = self.client.get(url)
        # 404 porque no hay archivo PDF, pero la URL es válida
        self.assertEqual(response.status_code, 404)

    def test_verify_url_with_valid_uuid(self):
        """Verifica que la URL de verificación acepta UUID válido"""
        url = reverse('certificates:verify', kwargs={'uuid': self.certificate.uuid})
        self.assertIn(str(self.certificate.uuid), url)
        
        # Verificar que la URL es accesible
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_query_url_accepts_post_with_dni(self):
        """Verifica que la URL de consulta acepta POST con DNI"""
        url = reverse('certificates:query')
        response = self.client.post(url, {'dni': '87654321'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'María García')


class MediaServingTest(TestCase):
    """Tests para verificar que los archivos media se sirven correctamente en desarrollo"""

    def test_media_url_configured(self):
        """Verifica que MEDIA_URL está configurado"""
        from django.conf import settings
        self.assertTrue(hasattr(settings, 'MEDIA_URL'))
        self.assertEqual(settings.MEDIA_URL, '/media/')

    def test_media_root_configured(self):
        """Verifica que MEDIA_ROOT está configurado"""
        from django.conf import settings
        self.assertTrue(hasattr(settings, 'MEDIA_ROOT'))
        self.assertIsNotNone(settings.MEDIA_ROOT)


class URLNamespaceTest(TestCase):
    """Tests para verificar que el namespace de URLs funciona correctamente"""

    def test_app_namespace_is_certificates(self):
        """Verifica que el namespace de la app es 'certificates'"""
        # Todas las URLs deben ser accesibles con el namespace 'certificates:'
        urls_to_test = [
            'certificates:import_excel',
            'certificates:query',
        ]
        
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                self.assertIsNotNone(url)
            except Exception as e:
                self.fail(f"URL {url_name} no se pudo resolver: {e}")

    def test_urls_with_parameters_use_namespace(self):
        """Verifica que las URLs con parámetros usan el namespace correctamente"""
        test_uuid = uuid.uuid4()
        
        # Download URL
        download_url = reverse('certificates:download', kwargs={'uuid': test_uuid})
        self.assertIsNotNone(download_url)
        
        # Verify URL
        verify_url = reverse('certificates:verify', kwargs={'uuid': test_uuid})
        self.assertIsNotNone(verify_url)


class URLIntegrationTest(TestCase):
    """Tests de integración para verificar el flujo completo de URLs"""

    def setUp(self):
        """Configuración inicial"""
        self.staff_user = User.objects.create_user(
            username='staff',
            password='testpass123',
            is_staff=True
        )
        
        self.event = Event.objects.create(
            name='Capacitación Django',
            event_date=date(2024, 2, 20)
        )
        
        self.participant = Participant.objects.create(
            dni='11223344',
            full_name='Carlos Rodríguez',
            event=self.event,
            attendee_type='ASISTENTE'
        )
        
        self.certificate = Certificate.objects.create(
            participant=self.participant,
            verification_url=f'http://testserver/verificar/{uuid.uuid4()}/'
        )

    def test_full_workflow_urls(self):
        """Verifica el flujo completo: importar -> consultar -> verificar"""
        # 1. Acceder a importación (requiere staff)
        self.client.login(username='staff', password='testpass123')
        import_url = reverse('certificates:import_excel')
        response = self.client.get(import_url)
        self.assertEqual(response.status_code, 200)
        
        # 2. Consultar certificado por DNI (público)
        self.client.logout()
        query_url = reverse('certificates:query')
        response = self.client.post(query_url, {'dni': '11223344'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Carlos Rodríguez')
        
        # 3. Verificar certificado (público)
        verify_url = reverse('certificates:verify', kwargs={'uuid': self.certificate.uuid})
        response = self.client.get(verify_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Carlos Rodríguez')
        self.assertContains(response, '11223344')

    def test_all_urls_return_valid_responses(self):
        """Verifica que todas las URLs retornan respuestas válidas"""
        # Login como staff para URLs protegidas
        self.client.login(username='staff', password='testpass123')
        
        # Test import URL
        import_url = reverse('certificates:import_excel')
        response = self.client.get(import_url)
        self.assertIn(response.status_code, [200, 302])
        
        # Logout para URLs públicas
        self.client.logout()
        
        # Test query URL
        query_url = reverse('certificates:query')
        response = self.client.get(query_url)
        self.assertEqual(response.status_code, 200)
        
        # Test verify URL
        verify_url = reverse('certificates:verify', kwargs={'uuid': self.certificate.uuid})
        response = self.client.get(verify_url)
        self.assertEqual(response.status_code, 200)
        
        # Test download URL (404 esperado sin archivo)
        download_url = reverse('certificates:download', kwargs={'uuid': self.certificate.uuid})
        response = self.client.get(download_url)
        self.assertEqual(response.status_code, 404)
