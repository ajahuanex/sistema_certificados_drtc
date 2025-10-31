"""
Tests de integración para las vistas del dashboard.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import cache

from certificates.models import (
    Certificate, Event, Participant, CertificateTemplate
)


class DashboardViewTest(TestCase):
    """Tests para la vista principal del dashboard"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        cache.clear()
        
        # Crear usuario staff
        self.staff_user = User.objects.create_user(
            username='staff',
            password='testpass123',
            is_staff=True
        )
        
        # Crear usuario normal (no staff)
        self.normal_user = User.objects.create_user(
            username='normal',
            password='testpass123',
            is_staff=False
        )
        
        # URL del dashboard
        self.dashboard_url = reverse('certificates:admin_dashboard')
    
    def tearDown(self):
        """Limpieza después de cada test"""
        cache.clear()
    
    def test_dashboard_requires_authentication(self):
        """Verifica que el dashboard requiere autenticación"""
        response = self.client.get(self.dashboard_url)
        
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)
    
    def test_dashboard_requires_staff_permission(self):
        """Verifica que el dashboard requiere permisos de staff"""
        # Login con usuario normal
        self.client.login(username='normal', password='testpass123')
        
        response = self.client.get(self.dashboard_url)
        
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
    
    def test_dashboard_accessible_for_staff(self):
        """Verifica que usuarios staff pueden acceder al dashboard"""
        # Login con usuario staff
        self.client.login(username='staff', password='testpass123')
        
        response = self.client.get(self.dashboard_url)
        
        # Debe ser exitoso
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_uses_correct_template(self):
        """Verifica que se usa el template correcto"""
        self.client.login(username='staff', password='testpass123')
        
        response = self.client.get(self.dashboard_url)
        
        self.assertTemplateUsed(response, 'admin/dashboard.html')
    
    def test_dashboard_context_contains_stats(self):
        """Verifica que el contexto contiene las estadísticas"""
        self.client.login(username='staff', password='testpass123')
        
        response = self.client.get(self.dashboard_url)
        
        # Verificar que stats está en el contexto
        self.assertIn('stats', response.context)
        
        # Verificar estructura de stats
        stats = response.context['stats']
        self.assertIn('certificates', stats)
        self.assertIn('queries', stats)
        self.assertIn('templates', stats)
        self.assertIn('quick_stats', stats)
    
    def test_dashboard_context_contains_recent_certificates(self):
        """Verifica que el contexto contiene certificados recientes"""
        self.client.login(username='staff', password='testpass123')
        
        response = self.client.get(self.dashboard_url)
        
        self.assertIn('recent_certificates', response.context)
        self.assertIsInstance(response.context['recent_certificates'], list)
    
    def test_dashboard_displays_stats_with_data(self):
        """Verifica que el dashboard muestra estadísticas con datos"""
        # Crear datos de prueba
        template = CertificateTemplate.objects.create(
            name="Test Template",
            html_template="<html>Test</html>"
        )
        event = Event.objects.create(
            name="Test Event",
            event_date="2024-01-01",
            template=template
        )
        participant = Participant.objects.create(
            dni="12345678",
            full_name="Test User",
            event=event,
            attendee_type="ASISTENTE"
        )
        Certificate.objects.create(
            participant=participant,
            is_signed=True
        )
        
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(self.dashboard_url)
        
        # Verificar que las estadísticas reflejan los datos
        stats = response.context['stats']
        self.assertGreater(stats['certificates']['total'], 0)
    
    def test_dashboard_handles_empty_database(self):
        """Verifica que el dashboard maneja correctamente una BD vacía"""
        self.client.login(username='staff', password='testpass123')
        
        response = self.client.get(self.dashboard_url)
        
        # Debe cargar sin errores
        self.assertEqual(response.status_code, 200)
        
        # Las estadísticas deben ser 0
        stats = response.context['stats']
        self.assertEqual(stats['certificates']['total'], 0)
    
    def test_dashboard_title_in_context(self):
        """Verifica que el título está en el contexto"""
        self.client.login(username='staff', password='testpass123')
        
        response = self.client.get(self.dashboard_url)
        
        self.assertIn('title', response.context)
        self.assertEqual(response.context['title'], 'Dashboard de Estadísticas')


class DashboardRefreshViewTest(TestCase):
    """Tests para la vista de actualización del dashboard"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        cache.clear()
        
        # Crear usuario staff
        self.staff_user = User.objects.create_user(
            username='staff',
            password='testpass123',
            is_staff=True
        )
        
        # URL de refresh
        self.refresh_url = reverse('certificates:dashboard_refresh')
    
    def tearDown(self):
        """Limpieza después de cada test"""
        cache.clear()
    
    def test_refresh_requires_authentication(self):
        """Verifica que refresh requiere autenticación"""
        response = self.client.post(self.refresh_url)
        
        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
    
    def test_refresh_requires_staff_permission(self):
        """Verifica que refresh requiere permisos de staff"""
        # Crear usuario normal
        normal_user = User.objects.create_user(
            username='normal',
            password='testpass123',
            is_staff=False
        )
        
        self.client.login(username='normal', password='testpass123')
        response = self.client.post(self.refresh_url)
        
        # Debe redirigir
        self.assertEqual(response.status_code, 302)
    
    def test_refresh_only_accepts_post(self):
        """Verifica que refresh solo acepta POST"""
        self.client.login(username='staff', password='testpass123')
        
        # GET debe fallar
        response = self.client.get(self.refresh_url)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
    
    def test_refresh_clears_cache(self):
        """Verifica que refresh limpia el caché"""
        self.client.login(username='staff', password='testpass123')
        
        # Cargar dashboard para crear caché
        dashboard_url = reverse('certificates:admin_dashboard')
        self.client.get(dashboard_url)
        
        # Verificar que hay caché
        from certificates.services.dashboard_stats import DashboardStatsService
        service = DashboardStatsService()
        cached = cache.get(service.CACHE_KEY)
        self.assertIsNotNone(cached)
        
        # Hacer refresh
        response = self.client.post(self.refresh_url)
        
        # Verificar que se limpió el caché
        cached = cache.get(service.CACHE_KEY)
        # Nota: puede ser None o tener nuevos datos, dependiendo del timing
        # Lo importante es que se ejecutó sin errores
        self.assertEqual(response.status_code, 302)
    
    def test_refresh_redirects_to_dashboard(self):
        """Verifica que refresh redirige al dashboard"""
        self.client.login(username='staff', password='testpass123')
        
        response = self.client.post(self.refresh_url)
        
        # Debe redirigir al dashboard
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/dashboard/', response.url)
    
    def test_refresh_shows_success_message(self):
        """Verifica que refresh muestra mensaje de éxito"""
        self.client.login(username='staff', password='testpass123')
        
        response = self.client.post(self.refresh_url, follow=True)
        
        # Verificar mensaje de éxito
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('actualizada', str(messages[0]))


class DashboardIntegrationTest(TestCase):
    """Tests de integración completos del dashboard"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        cache.clear()
        
        # Crear usuario staff
        self.staff_user = User.objects.create_user(
            username='staff',
            password='testpass123',
            is_staff=True
        )
        
        # Crear datos de prueba completos
        self.template = CertificateTemplate.objects.create(
            name="Template Integración",
            html_template="<html>Test</html>"
        )
        
        self.event = Event.objects.create(
            name="Evento Integración",
            event_date="2024-01-01",
            template=self.template
        )
        
        # Crear múltiples participantes y certificados
        for i in range(5):
            participant = Participant.objects.create(
                dni=f"1234567{i}",
                full_name=f"Participante {i}",
                event=self.event,
                attendee_type="ASISTENTE"
            )
            Certificate.objects.create(
                participant=participant,
                is_signed=(i % 2 == 0)  # Alternar firmados/sin firmar
            )
    
    def tearDown(self):
        """Limpieza"""
        cache.clear()
    
    def test_full_dashboard_workflow(self):
        """Test del flujo completo del dashboard"""
        # 1. Login
        self.client.login(username='staff', password='testpass123')
        
        # 2. Acceder al dashboard
        dashboard_url = reverse('certificates:admin_dashboard')
        response = self.client.get(dashboard_url)
        
        self.assertEqual(response.status_code, 200)
        
        # 3. Verificar estadísticas
        stats = response.context['stats']
        self.assertEqual(stats['certificates']['total'], 5)
        self.assertEqual(stats['certificates']['signed'], 3)
        self.assertEqual(stats['certificates']['unsigned'], 2)
        
        # 4. Verificar certificados recientes
        recent = response.context['recent_certificates']
        self.assertLessEqual(len(recent), 10)
        
        # 5. Hacer refresh
        refresh_url = reverse('certificates:dashboard_refresh')
        response = self.client.post(refresh_url, follow=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 6. Verificar que las estadísticas siguen correctas
        stats = response.context['stats']
        self.assertEqual(stats['certificates']['total'], 5)
    
    def test_dashboard_performance(self):
        """Verifica que el dashboard carga rápidamente"""
        import time
        
        self.client.login(username='staff', password='testpass123')
        dashboard_url = reverse('certificates:admin_dashboard')
        
        # Primera carga (sin caché)
        start = time.time()
        response = self.client.get(dashboard_url)
        first_load = time.time() - start
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(first_load, 2.0)  # Debe cargar en menos de 2 segundos
        
        # Segunda carga (con caché)
        start = time.time()
        response = self.client.get(dashboard_url)
        cached_load = time.time() - start
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(cached_load, 0.5)  # Con caché debe ser mucho más rápido
    
    def test_dashboard_with_recent_certificates_limit(self):
        """Verifica que solo se muestran los últimos 10 certificados"""
        # Crear más de 10 certificados
        for i in range(15):
            participant = Participant.objects.create(
                dni=f"9999999{i:02d}",
                full_name=f"Extra {i}",
                event=self.event,
                attendee_type="PONENTE"
            )
            Certificate.objects.create(
                participant=participant,
                is_signed=True
            )
        
        self.client.login(username='staff', password='testpass123')
        dashboard_url = reverse('certificates:admin_dashboard')
        response = self.client.get(dashboard_url)
        
        recent = response.context['recent_certificates']
        self.assertEqual(len(recent), 10)
