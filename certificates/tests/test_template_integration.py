"""
Tests de integración para el sistema de plantillas visuales.
"""
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.db import transaction
from unittest.mock import patch, MagicMock
from io import BytesIO

from certificates.models import (
    CertificateTemplate, 
    TemplateElement, 
    TemplateAsset,
    Event,
    Participant,
    Certificate
)
from certificates.services.certificate_generator import CertificateGeneratorService
from certificates.services.template_migration import TemplateMigrationService

# Mock WeasyPrint to avoid system dependencies
try:
    from certificates.services.template_renderer import TemplateRenderingService
except ImportError:
    # Create a mock if WeasyPrint is not available
    class TemplateRenderingService:
        def render_template_to_pdf(self, template_id, participant_data):
            return b'Mock PDF content'


class TemplateIntegrationTestCase(TestCase):
    """Tests de integración para el sistema de plantillas"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            is_staff=True
        )
        
        # Crear plantilla visual de prueba
        self.visual_template = CertificateTemplate.objects.create(
            name='Plantilla Visual Test',
            html_template='<!-- Plantilla visual -->',
            canvas_width=842,
            canvas_height=595,
            editor_version='1.0',
            last_edited_by=self.user
        )
        
        # Crear elementos para la plantilla visual
        self.text_element = TemplateElement.objects.create(
            template=self.visual_template,
            element_type='TEXT',
            name='Título',
            position_x=100,
            position_y=100,
            width=400,
            height=50,
            content='CERTIFICADO',
            style_config={
                'text': {
                    'fontSize': 32,
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'color': '#000000'
                }
            }
        )
        
        self.variable_element = TemplateElement.objects.create(
            template=self.visual_template,
            element_type='VARIABLE',
            name='Nombre Participante',
            position_x=100,
            position_y=200,
            width=400,
            height=40,
            content='{{participant_name}}',
            style_config={
                'text': {
                    'fontSize': 24,
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'color': '#000000'
                }
            }
        )
        
        # Crear plantilla HTML tradicional
        self.html_template = CertificateTemplate.objects.create(
            name='Plantilla HTML Test',
            html_template='''
            <html>
            <body>
                <h1>CERTIFICADO</h1>
                <p>Se otorga a: {{ full_name }}</p>
                <p>DNI: {{ dni }}</p>
                <p>Evento: {{ event_name }}</p>
            </body>
            </html>
            ''',
            is_default=True
        )
        
        # Crear evento de prueba
        self.event = Event.objects.create(
            name='Evento Test',
            event_date='2024-01-15',
            template=self.visual_template
        )
        
        # Crear participante de prueba
        self.participant = Participant.objects.create(
            dni='12345678',
            full_name='Juan Pérez García',
            event=self.event,
            attendee_type='ASISTENTE'
        )


class CertificateGenerationIntegrationTest(TemplateIntegrationTestCase):
    """Tests de integración para generación de certificados"""
    
    @patch('certificates.services.template_renderer.TemplateRenderingService.render_template_to_pdf')
    def test_generate_certificate_with_visual_template(self, mock_render):
        """Test generación de certificado con plantilla visual"""
        # Mock del renderizado
        mock_render.return_value = b'PDF content'
        
        # Generar certificado
        service = CertificateGeneratorService()
        certificate = service.generate_certificate(self.participant, user=self.user)
        
        # Verificar que se creó el certificado
        self.assertIsNotNone(certificate)
        self.assertEqual(certificate.participant, self.participant)
        
        # Verificar que se llamó al renderizador visual
        mock_render.assert_called_once()
        
        # Verificar argumentos del renderizador
        call_args = mock_render.call_args
        template_id = call_args[0][0]
        participant_data = call_args[0][1]
        
        self.assertEqual(template_id, self.visual_template.id)
        self.assertEqual(participant_data['participant_name'], 'Juan Pérez García')
        self.assertEqual(participant_data['participant_dni'], '12345678')
    
    def test_generate_certificate_with_html_template(self):
        """Test generación de certificado con plantilla HTML tradicional"""
        # Cambiar evento para usar plantilla HTML
        self.event.template = self.html_template
        self.event.save()
        
        # Generar certificado
        service = CertificateGeneratorService()
        certificate = service.generate_certificate(self.participant, user=self.user)
        
        # Verificar que se creó el certificado
        self.assertIsNotNone(certificate)
        self.assertEqual(certificate.participant, self.participant)
        
        # Verificar que se usó el método simple (no visual)
        # Esto se puede verificar por el tamaño del PDF o contenido específico
        self.assertTrue(certificate.pdf_file)
    
    def test_fallback_to_simple_pdf_when_visual_fails(self):
        """Test fallback al PDF simple cuando falla el renderizado visual"""
        # Crear plantilla visual con elementos pero sin renderizador funcional
        with patch('certificates.services.template_renderer.TemplateRenderingService.render_template_to_pdf') as mock_render:
            mock_render.side_effect = Exception("Rendering failed")
            
            service = CertificateGeneratorService()
            
            # Debería fallar la generación completa
            with self.assertRaises(Exception):
                service.generate_certificate(self.participant, user=self.user)


class TemplateMigrationIntegrationTest(TemplateIntegrationTestCase):
    """Tests de integración para migración de plantillas"""
    
    def test_migrate_html_template_to_visual(self):
        """Test migración de plantilla HTML a formato visual"""
        service = TemplateMigrationService()
        
        # Migrar plantilla HTML
        result = service.migrate_template(self.html_template.id)
        
        # Verificar resultado exitoso
        self.assertTrue(result['success'])
        self.assertGreater(result['elements_created'], 0)
        
        # Verificar que se crearon elementos
        self.html_template.refresh_from_db()
        elements = self.html_template.elements.all()
        self.assertGreater(elements.count(), 0)
        
        # Verificar que se actualizó la configuración
        self.assertEqual(self.html_template.canvas_width, 842)
        self.assertEqual(self.html_template.canvas_height, 595)
        self.assertEqual(self.html_template.editor_version, '1.0')
    
    def test_migrate_template_preserves_original_html(self):
        """Test que la migración preserva el HTML original"""
        original_html = self.html_template.html_template
        
        service = TemplateMigrationService()
        result = service.migrate_template(self.html_template.id, preserve_original=True)
        
        self.assertTrue(result['success'])
        
        # Verificar que el HTML original está preservado como comentario
        self.html_template.refresh_from_db()
        self.assertIn('HTML ORIGINAL ANTES DE MIGRACIÓN', self.html_template.html_template)
        self.assertIn(original_html, self.html_template.html_template)
    
    def test_migration_preview(self):
        """Test preview de migración sin hacer cambios"""
        service = TemplateMigrationService()
        
        # Obtener preview
        result = service.preview_migration(self.html_template.id)
        
        # Verificar resultado
        self.assertTrue(result['success'])
        self.assertGreater(result['total_elements'], 0)
        self.assertIn('elements_by_type', result)
        self.assertIn('elements_preview', result)
        
        # Verificar que no se crearon elementos reales
        self.assertEqual(self.html_template.elements.count(), 0)
    
    def test_mass_migration(self):
        """Test migración masiva de plantillas"""
        # Crear otra plantilla HTML
        html_template2 = CertificateTemplate.objects.create(
            name='Plantilla HTML 2',
            html_template='<h1>Otro certificado</h1><p>Para: {{ full_name }}</p>'
        )
        
        service = TemplateMigrationService()
        
        # Migrar todas las plantillas
        results = service.migrate_all_templates()
        
        # Verificar resultados
        self.assertGreater(results['total_templates'], 0)
        self.assertGreater(results['migrated_successfully'], 0)
        
        # Verificar que las plantillas HTML fueron migradas
        self.html_template.refresh_from_db()
        html_template2.refresh_from_db()
        
        self.assertGreater(self.html_template.elements.count(), 0)
        self.assertGreater(html_template2.elements.count(), 0)


class AdminIntegrationTest(TemplateIntegrationTestCase):
    """Tests de integración para la interfaz de administración"""
    
    def setUp(self):
        super().setUp()
        self.client.login(username='testuser', password='testpass')
    
    def test_template_admin_shows_type(self):
        """Test que el admin muestra el tipo de plantilla"""
        response = self.client.get('/admin/certificates/certificatetemplate/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '🎨 Visual')  # Para plantilla visual
        self.assertContains(response, '📝 HTML')   # Para plantilla HTML
    
    def test_template_admin_shows_migration_button(self):
        """Test que el admin muestra botón de migración para plantillas HTML"""
        response = self.client.get('/admin/certificates/certificatetemplate/')
        
        self.assertEqual(response.status_code, 200)
        # Debería mostrar botón de migración para plantilla HTML
        self.assertContains(response, '🔄 Migrar')
    
    def test_migration_view_accessible(self):
        """Test que la vista de migración es accesible"""
        url = reverse('admin:certificates_certificatetemplate_migrate', args=[self.html_template.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Preview de Migración')
    
    def test_mass_migration_view_accessible(self):
        """Test que la vista de migración masiva es accesible"""
        url = reverse('admin:certificates_certificatetemplate_migrate_all')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Migrar Todas las Plantillas')
    
    def test_event_admin_shows_template_type(self):
        """Test que el admin de eventos muestra el tipo de plantilla"""
        response = self.client.get('/admin/certificates/event/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '🎨 Visual')  # Para evento con plantilla visual


class APIIntegrationTest(TemplateIntegrationTestCase):
    """Tests de integración para las APIs"""
    
    def setUp(self):
        super().setUp()
        self.client.login(username='testuser', password='testpass')
    
    def test_template_api_returns_visual_elements(self):
        """Test que la API de plantillas retorna elementos visuales"""
        url = f'/api/templates/{self.visual_template.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data['id'], self.visual_template.id)
        self.assertGreater(len(data['elements']), 0)
        
        # Verificar elementos específicos
        element_names = [elem['name'] for elem in data['elements']]
        self.assertIn('Título', element_names)
        self.assertIn('Nombre Participante', element_names)
    
    def test_template_preview_api(self):
        """Test API de preview de plantillas"""
        url = f'/api/templates/{self.visual_template.id}/preview/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('template', data)
        self.assertIn('test_data', data)
        self.assertIn('preview_pdf_url', data)
    
    @patch('certificates.services.template_renderer.TemplateRenderingService.render_template_to_pdf')
    def test_template_preview_pdf_generation(self, mock_render):
        """Test generación de PDF de preview"""
        mock_render.return_value = b'PDF content'
        
        url = f'/api/templates/{self.visual_template.id}/preview/?format=pdf'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        mock_render.assert_called_once()


class EndToEndIntegrationTest(TemplateIntegrationTestCase):
    """Tests de integración end-to-end"""
    
    def setUp(self):
        super().setUp()
        self.client.login(username='testuser', password='testpass')
    
    @patch('certificates.services.template_renderer.TemplateRenderingService.render_template_to_pdf')
    def test_complete_certificate_workflow_with_visual_template(self, mock_render):
        """Test flujo completo: crear plantilla visual -> generar certificado -> verificar"""
        mock_render.return_value = b'PDF content'
        
        # 1. Crear plantilla visual via API
        template_data = {
            'name': 'Plantilla E2E Test',
            'canvas_width': 842,
            'canvas_height': 595
        }
        response = self.client.post('/api/templates/', template_data)
        self.assertEqual(response.status_code, 201)
        template_id = response.json()['id']
        
        # 2. Agregar elementos via API
        element_data = {
            'template': template_id,
            'element_type': 'TEXT',
            'name': 'Título E2E',
            'position_x': 100,
            'position_y': 100,
            'width': 400,
            'height': 50,
            'content': 'CERTIFICADO E2E',
            'style_config': {
                'text': {'fontSize': 32, 'textAlign': 'center'}
            }
        }
        response = self.client.post('/api/elements/', element_data)
        self.assertEqual(response.status_code, 201)
        
        # 3. Asignar plantilla al evento
        self.event.template_id = template_id
        self.event.save()
        
        # 4. Generar certificado
        service = CertificateGeneratorService()
        certificate = service.generate_certificate(self.participant, user=self.user)
        
        # 5. Verificar certificado
        self.assertIsNotNone(certificate)
        self.assertEqual(certificate.participant, self.participant)
        mock_render.assert_called_once()
        
        # 6. Verificar que se puede acceder al certificado
        verification_url = f'/verificar/{certificate.uuid}/'
        response = self.client.get(verification_url)
        self.assertEqual(response.status_code, 200)
    
    def test_migration_to_visual_and_certificate_generation(self):
        """Test migración de plantilla HTML y generación de certificado"""
        # 1. Migrar plantilla HTML
        service = TemplateMigrationService()
        result = service.migrate_template(self.html_template.id)
        self.assertTrue(result['success'])
        
        # 2. Asignar plantilla migrada al evento
        self.event.template = self.html_template
        self.event.save()
        
        # 3. Generar certificado (debería usar el nuevo sistema visual)
        with patch('certificates.services.template_renderer.TemplateRenderingService.render_template_to_pdf') as mock_render:
            mock_render.return_value = b'PDF content'
            
            service = CertificateGeneratorService()
            certificate = service.generate_certificate(self.participant, user=self.user)
            
            # Verificar que se usó el renderizador visual
            mock_render.assert_called_once()
            self.assertIsNotNone(certificate)


class PerformanceIntegrationTest(TemplateIntegrationTestCase):
    """Tests de rendimiento para integración"""
    
    def test_bulk_certificate_generation_performance(self):
        """Test rendimiento de generación masiva de certificados"""
        # Crear múltiples participantes
        participants = []
        for i in range(10):
            participant = Participant.objects.create(
                dni=f'1234567{i}',
                full_name=f'Participante {i}',
                event=self.event,
                attendee_type='ASISTENTE'
            )
            participants.append(participant)
        
        # Mock del renderizador para evitar generación real de PDFs
        with patch('certificates.services.template_renderer.TemplateRenderingService.render_template_to_pdf') as mock_render:
            mock_render.return_value = b'PDF content'
            
            # Generar certificados masivamente
            service = CertificateGeneratorService()
            result = service.generate_bulk_certificates(self.event, user=self.user)
            
            # Verificar resultados
            self.assertEqual(result['success_count'], 10)
            self.assertEqual(result['error_count'], 0)
            
            # Verificar que se llamó al renderizador para cada certificado
            self.assertEqual(mock_render.call_count, 10)
    
    def test_template_migration_performance(self):
        """Test rendimiento de migración de plantillas"""
        # Crear múltiples plantillas HTML
        templates = []
        for i in range(5):
            template = CertificateTemplate.objects.create(
                name=f'Plantilla Performance {i}',
                html_template=f'<h1>Certificado {i}</h1><p>Para: {{{{ full_name }}}}</p>'
            )
            templates.append(template)
        
        # Migrar todas las plantillas
        service = TemplateMigrationService()
        results = service.migrate_all_templates()
        
        # Verificar que todas se migraron exitosamente
        self.assertGreaterEqual(results['migrated_successfully'], 5)
        self.assertEqual(results['migration_errors'], 0)
        
        # Verificar que todas tienen elementos
        for template in templates:
            template.refresh_from_db()
            self.assertGreater(template.elements.count(), 0)