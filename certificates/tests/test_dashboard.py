"""Tests para el dashboard de estadísticas"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import json

from certificates.models import Event, Participant, Certificate, CertificateTemplate, AuditLog


class DashboardViewTest(TestCase):
    """Tests para la vista principal del dashboard"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        # Crear usuario administrador
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # Crear cliente y hacer login
        self.client = Client()
        self.client.login(username='admin', password='testpass123')
        
        # Crear datos de prueba
        self.create_test_data()
    
    def create_test_data(self):
        """Crea datos de prueba para los tests"""
        # Crear plantilla por defecto
        self.template = CertificateTemplate.objects.create(
            name="Plantilla Test",
            html_template="<html>Test</html>",
            is_default=True
        )
        
        # Crear eventos
        self.event1 = Event.objects.create(
            name="Evento Test 1",
            event_date=timezone.now().date(),
            template=self.template
        )
        
        self.event2 = Event.objects.create(
            name="Evento Test 2",
            event_date=timezone.now().date() - timedelta(days=30),
            template=self.template
        )
        
        # Crear participantes
        self.participant1 = Participant.objects.create(
            dni="12345678",
            full_name="Juan Pérez",
            event=self.event1,
            attendee_type="ASISTENTE"
        )
        
        self.participant2 = Participant.objects.create(
            dni="87654321",
            full_name="María García",
            event=self.event1,
            attendee_type="PONENTE"
        )
        
        self.participant3 = Participant.objects.create(
            dni="11223344",
            full_name="Carlos López",
            event=self.event2,
            attendee_type="ORGANIZADOR"
        )
        
        # Crear certificados
        self.certificate1 = Certificate.objects.create(
            participant=self.participant1,
            pdf_file="test1.pdf",
            qr_code="test1.png",
            verification_url="http://test.com/verify/1",
            is_signed=True,
            signed_at=timezone.now()
        )
        
        self.certificate2 = Certificate.objects.create(
            participant=self.participant2,
            pdf_file="test2.pdf",
            qr_code="test2.png",
            verification_url="http://test.com/verify/2",
            is_signed=False
        )
        
        # Crear logs de auditoría
        AuditLog.objects.create(
            action_type='IMPORT',
            user=self.admin_user,
            description='Test import',
            ip_address='127.0.0.1'
        )
        
        AuditLog.objects.create(
            action_type='VERIFY',
            description='Test verification',
            ip_address='192.168.1.1'
        )
    
    def test_dashboard_view_requires_staff(self):
        """Test que el dashboard requiere permisos de staff"""
        # Crear usuario normal (no staff)
        normal_user = User.objects.create_user(
            username='normal',
            password='testpass123'
        )
        
        client = Client()
        client.login(username='normal', password='testpass123')
        
        response = client.get(reverse('certificates:dashboard'))
        
        # Debe redirigir al login del admin
        self.assertEqual(response.status_code, 302)
    
    def test_dashboard_view_loads_successfully(self):
        """Test que el dashboard carga correctamente para staff"""
        response = self.client.get(reverse('certificates:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard de Certificados')
        self.assertContains(response, 'Total de Eventos')
        self.assertContains(response, 'Certificados Generados')
    
    def test_dashboard_shows_correct_statistics(self):
        """Test que el dashboard muestra estadísticas correctas"""
        response = self.client.get(reverse('certificates:dashboard'))
        
        # Verificar contexto
        self.assertEqual(response.context['total_events'], 2)
        self.assertEqual(response.context['total_participants'], 3)
        self.assertEqual(response.context['total_certificates'], 2)
        self.assertEqual(response.context['signed_certificates'], 1)
        self.assertEqual(response.context['pending_certificates'], 1)
    
    def test_dashboard_shows_recent_events(self):
        """Test que el dashboard muestra eventos recientes"""
        response = self.client.get(reverse('certificates:dashboard'))
        
        recent_events = response.context['recent_events']
        self.assertEqual(len(recent_events), 2)
        
        # Debe estar ordenado por fecha de creación descendente
        self.assertEqual(recent_events[0], self.event1)
    
    def test_dashboard_shows_recent_certificates(self):
        """Test que el dashboard muestra certificados recientes"""
        response = self.client.get(reverse('certificates:dashboard'))
        
        recent_certificates = response.context['recent_certificates']
        self.assertEqual(len(recent_certificates), 2)
    
    def test_dashboard_shows_attendee_statistics(self):
        """Test que el dashboard muestra estadísticas por tipo de asistente"""
        response = self.client.get(reverse('certificates:dashboard'))
        
        attendee_stats = response.context['attendee_stats']
        
        # Verificar que hay estadísticas para cada tipo
        types = [stat['attendee_type'] for stat in attendee_stats]
        self.assertIn('ASISTENTE', types)
        self.assertIn('PONENTE', types)
        self.assertIn('ORGANIZADOR', types)
    
    def test_dashboard_shows_recent_activity(self):
        """Test que el dashboard muestra actividad reciente"""
        response = self.client.get(reverse('certificates:dashboard'))
        
        recent_activity = response.context['recent_activity']
        self.assertEqual(len(recent_activity), 2)
        
        # Verificar que incluye los logs creados
        action_types = [log.action_type for log in recent_activity]
        self.assertIn('IMPORT', action_types)
        self.assertIn('VERIFY', action_types)


class DashboardChartsAPITest(TestCase):
    """Tests para la API de gráficos del dashboard"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_staff=True
        )
        
        self.client = Client()
        self.client.login(username='admin', password='testpass123')
        
        # Crear datos de prueba
        self.create_test_data()
    
    def create_test_data(self):
        """Crea datos de prueba para los gráficos"""
        template = CertificateTemplate.objects.create(
            name="Test Template",
            html_template="<html>Test</html>",
            is_default=True
        )
        
        # Crear eventos en diferentes meses
        event1 = Event.objects.create(
            name="Evento Mes Actual",
            event_date=timezone.now().date(),
            template=template
        )
        
        event2 = Event.objects.create(
            name="Evento Mes Pasado",
            event_date=(timezone.now() - timedelta(days=30)).date(),
            template=template
        )
        
        # Crear participantes
        participant1 = Participant.objects.create(
            dni="12345678",
            full_name="Test User 1",
            event=event1,
            attendee_type="ASISTENTE"
        )
        
        participant2 = Participant.objects.create(
            dni="87654321",
            full_name="Test User 2",
            event=event2,
            attendee_type="PONENTE"
        )
        
        # Crear certificados
        Certificate.objects.create(
            participant=participant1,
            pdf_file="test1.pdf",
            qr_code="test1.png",
            verification_url="http://test.com/1",
            is_signed=True
        )
        
        Certificate.objects.create(
            participant=participant2,
            pdf_file="test2.pdf",
            qr_code="test2.png",
            verification_url="http://test.com/2",
            is_signed=False
        )
        
        # Crear logs de verificación
        AuditLog.objects.create(
            action_type='VERIFY',
            description='Test verification 1',
            timestamp=timezone.now()
        )
        
        AuditLog.objects.create(
            action_type='VERIFY',
            description='Test verification 2',
            timestamp=timezone.now() - timedelta(days=1)
        )
    
    def test_certificates_by_month_chart(self):
        """Test del gráfico de certificados por mes"""
        response = self.client.get(
            reverse('certificates:dashboard_charts'),
            {'chart': 'certificates_by_month'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('labels', data)
        self.assertIn('datasets', data)
        self.assertEqual(len(data['datasets']), 1)
        self.assertEqual(data['datasets'][0]['label'], 'Certificados Generados')
    
    def test_events_by_month_chart(self):
        """Test del gráfico de eventos por mes"""
        response = self.client.get(
            reverse('certificates:dashboard_charts'),
            {'chart': 'events_by_month'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('labels', data)
        self.assertIn('datasets', data)
        self.assertEqual(data['datasets'][0]['label'], 'Eventos Creados')
    
    def test_verifications_by_day_chart(self):
        """Test del gráfico de verificaciones por día"""
        response = self.client.get(
            reverse('certificates:dashboard_charts'),
            {'chart': 'verifications_by_day'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('labels', data)
        self.assertIn('datasets', data)
        self.assertEqual(data['datasets'][0]['label'], 'Verificaciones')
    
    def test_attendee_types_chart(self):
        """Test del gráfico de tipos de asistentes"""
        response = self.client.get(
            reverse('certificates:dashboard_charts'),
            {'chart': 'attendee_types'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('labels', data)
        self.assertIn('datasets', data)
        
        # Verificar que incluye los tipos correctos
        self.assertIn('Asistentes', data['labels'])
        self.assertIn('Ponentes', data['labels'])
    
    def test_signature_status_chart(self):
        """Test del gráfico de estado de firmas"""
        response = self.client.get(
            reverse('certificates:dashboard_charts'),
            {'chart': 'signature_status'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('labels', data)
        self.assertIn('datasets', data)
        
        # Verificar etiquetas
        self.assertIn('Firmados Digitalmente', data['labels'])
        self.assertIn('Sin Firma', data['labels'])
        
        # Verificar datos (1 firmado, 1 sin firmar)
        self.assertEqual(data['datasets'][0]['data'], [1, 1])
    
    def test_invalid_chart_type(self):
        """Test con tipo de gráfico inválido"""
        response = self.client.get(
            reverse('certificates:dashboard_charts'),
            {'chart': 'invalid_chart'}
        )
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.content)
        self.assertIn('error', data)
    
    def test_charts_require_staff_permission(self):
        """Test que los gráficos requieren permisos de staff"""
        # Crear usuario normal
        normal_user = User.objects.create_user(
            username='normal',
            password='testpass123'
        )
        
        client = Client()
        client.login(username='normal', password='testpass123')
        
        response = client.get(
            reverse('certificates:dashboard_charts'),
            {'chart': 'certificates_by_month'}
        )
        
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)


class DashboardStatsAPITest(TestCase):
    """Tests para la API de estadísticas del dashboard"""
    
    def setUp(self):
        """Configuración inicial"""
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_staff=True
        )
        
        self.client = Client()
        self.client.login(username='admin', password='testpass123')
    
    def test_overview_stats(self):
        """Test de estadísticas generales"""
        response = self.client.get(
            reverse('certificates:dashboard_stats'),
            {'stat': 'overview'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('total_certificates', data)
        self.assertIn('certificates_last_month', data)
        self.assertIn('certificate_trend', data)
        self.assertIn('signature_rate', data)
    
    def test_performance_stats(self):
        """Test de estadísticas de performance"""
        response = self.client.get(
            reverse('certificates:dashboard_stats'),
            {'stat': 'performance'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('recent_activity', data)
        self.assertIn('popular_events', data)
        self.assertIn('total_activity_24h', data)
    
    def test_activity_stats(self):
        """Test de estadísticas de actividad"""
        response = self.client.get(
            reverse('certificates:dashboard_stats'),
            {'stat': 'activity'}
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('hourly_activity', data)
        self.assertIn('peak_hour', data)
        self.assertIn('total_activity_week', data)
    
    def test_invalid_stat_type(self):
        """Test con tipo de estadística inválido"""
        response = self.client.get(
            reverse('certificates:dashboard_stats'),
            {'stat': 'invalid_stat'}
        )
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.content)
        self.assertIn('error', data)


class DashboardIntegrationTest(TestCase):
    """Tests de integración del dashboard completo"""
    
    def setUp(self):
        """Configuración inicial"""
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_staff=True
        )
        
        self.client = Client()
        self.client.login(username='admin', password='testpass123')
        
        # Crear datos realistas
        self.create_realistic_data()
    
    def create_realistic_data(self):
        """Crea datos realistas para tests de integración"""
        template = CertificateTemplate.objects.create(
            name="Plantilla DRTC",
            html_template="<html><body>Certificado</body></html>",
            is_default=True
        )
        
        # Crear múltiples eventos
        events = []
        for i in range(5):
            event = Event.objects.create(
                name=f"Capacitación {i+1}",
                event_date=timezone.now().date() - timedelta(days=i*10),
                template=template
            )
            events.append(event)
        
        # Crear participantes y certificados
        attendee_types = ['ASISTENTE', 'PONENTE', 'ORGANIZADOR']
        for i, event in enumerate(events):
            for j in range(3):  # 3 participantes por evento
                participant = Participant.objects.create(
                    dni=f"{12345678 + i*10 + j}",
                    full_name=f"Participante {i}-{j}",
                    event=event,
                    attendee_type=attendee_types[j % 3]
                )
                
                Certificate.objects.create(
                    participant=participant,
                    pdf_file=f"cert_{i}_{j}.pdf",
                    qr_code=f"qr_{i}_{j}.png",
                    verification_url=f"http://test.com/{i}/{j}",
                    is_signed=(j % 2 == 0)  # Alternar firmados/sin firmar
                )
        
        # Crear actividad de auditoría
        actions = ['IMPORT', 'GENERATE', 'SIGN', 'VERIFY', 'QUERY']
        for i in range(20):
            AuditLog.objects.create(
                action_type=actions[i % 5],
                user=self.admin_user if i % 3 == 0 else None,
                description=f"Test action {i}",
                timestamp=timezone.now() - timedelta(hours=i)
            )
    
    def test_dashboard_with_realistic_data(self):
        """Test del dashboard con datos realistas"""
        response = self.client.get(reverse('certificates:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que las estadísticas son correctas
        self.assertEqual(response.context['total_events'], 5)
        self.assertEqual(response.context['total_participants'], 15)
        self.assertEqual(response.context['total_certificates'], 15)
        
        # Verificar que hay datos en todas las secciones
        self.assertTrue(len(response.context['recent_events']) > 0)
        self.assertTrue(len(response.context['recent_certificates']) > 0)
        self.assertTrue(len(response.context['attendee_stats']) > 0)
        self.assertTrue(len(response.context['recent_activity']) > 0)
    
    def test_all_charts_work_with_data(self):
        """Test que todos los gráficos funcionan con datos realistas"""
        chart_types = [
            'certificates_by_month',
            'events_by_month',
            'verifications_by_day',
            'attendee_types',
            'signature_status'
        ]
        
        for chart_type in chart_types:
            with self.subTest(chart_type=chart_type):
                response = self.client.get(
                    reverse('certificates:dashboard_charts'),
                    {'chart': chart_type}
                )
                
                self.assertEqual(response.status_code, 200)
                
                data = json.loads(response.content)
                self.assertIn('labels', data)
                self.assertIn('datasets', data)
                self.assertTrue(len(data['datasets']) > 0)
    
    def test_dashboard_performance(self):
        """Test de performance del dashboard"""
        from django.test.utils import override_settings
        from django.db import connection
        
        with override_settings(DEBUG=True):
            # Resetear queries
            connection.queries_log.clear()
            
            # Cargar dashboard
            response = self.client.get(reverse('certificates:dashboard'))
            
            self.assertEqual(response.status_code, 200)
            
            # Verificar que no hay demasiadas queries
            # (debería ser menos de 20 para un dashboard eficiente)
            num_queries = len(connection.queries)
            self.assertLess(num_queries, 20, 
                          f"Dashboard usa demasiadas queries: {num_queries}")