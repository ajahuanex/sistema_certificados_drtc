"""Tests para rate limiting en vistas públicas"""
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from certificates.models import Event, Participant, Certificate
from datetime import date
import uuid

User = get_user_model()


@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
})
class RateLimitingTestCase(TestCase):
    """Tests para verificar rate limiting en vistas públicas"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        # Limpiar cache antes de cada test
        cache.clear()
        
        # Crear evento de prueba
        self.event = Event.objects.create(
            name='Evento de Prueba',
            event_date=date(2024, 1, 15),
            description='Descripción del evento'
        )
        
        # Crear participante de prueba
        self.participant = Participant.objects.create(
            dni='12345678',
            full_name='Juan Pérez',
            event=self.event,
            attendee_type='ASISTENTE'
        )
        
        # Crear certificado de prueba
        self.certificate = Certificate.objects.create(
            participant=self.participant,
            verification_url=f'http://testserver/verificar/{uuid.uuid4()}/'
        )
    
    def tearDown(self):
        """Limpieza después de cada test"""
        cache.clear()
    
    def test_certificate_query_rate_limit(self):
        """Test que verifica el rate limit en CertificateQueryView (10 requests/minuto)"""
        url = reverse('certificates:query')
        
        # Realizar 10 solicitudes POST (el límite)
        for i in range(10):
            response = self.client.post(url, {'dni': '12345678'})
            self.assertIn(response.status_code, [200, 302], 
                         f"Request {i+1} should succeed")
        
        # La solicitud 11 debería ser bloqueada
        response = self.client.post(url, {'dni': '12345678'})
        self.assertEqual(response.status_code, 429, 
                        "Request 11 should be rate limited")
        self.assertIn('Límite de Solicitudes Excedido', response.content.decode())
    
    def test_certificate_query_rate_limit_get_not_limited(self):
        """Test que verifica que GET no está limitado en CertificateQueryView"""
        url = reverse('certificates:query')
        
        # Realizar 15 solicitudes GET (más que el límite de POST)
        for i in range(15):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, 
                           f"GET request {i+1} should not be rate limited")
    
    def test_certificate_verification_rate_limit(self):
        """Test que verifica el rate limit en CertificateVerificationView (20 requests/minuto)"""
        url = reverse('certificates:verify', kwargs={'uuid': self.certificate.uuid})
        
        # Realizar 20 solicitudes GET (el límite)
        for i in range(20):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, 
                           f"Request {i+1} should succeed")
        
        # La solicitud 21 debería ser bloqueada
        response = self.client.get(url)
        self.assertEqual(response.status_code, 429, 
                        "Request 21 should be rate limited")
        self.assertIn('Límite de Solicitudes Excedido', response.content.decode())
    
    def test_rate_limit_different_ips(self):
        """Test que verifica que el rate limit es por IP"""
        url = reverse('certificates:query')
        
        # Realizar 10 solicitudes desde una IP
        for i in range(10):
            response = self.client.post(url, {'dni': '12345678'}, 
                                       REMOTE_ADDR='192.168.1.1')
            self.assertIn(response.status_code, [200, 302])
        
        # La solicitud 11 desde la misma IP debería ser bloqueada
        response = self.client.post(url, {'dni': '12345678'}, 
                                   REMOTE_ADDR='192.168.1.1')
        self.assertEqual(response.status_code, 429)
        
        # Pero una solicitud desde otra IP debería funcionar
        response = self.client.post(url, {'dni': '12345678'}, 
                                   REMOTE_ADDR='192.168.1.2')
        self.assertIn(response.status_code, [200, 302], 
                     "Request from different IP should succeed")
    
    def test_rate_limit_error_message(self):
        """Test que verifica el mensaje de error cuando se excede el límite"""
        url = reverse('certificates:query')
        
        # Exceder el límite
        for i in range(11):
            response = self.client.post(url, {'dni': '12345678'})
        
        # Verificar que el mensaje de error está presente
        self.assertEqual(response.status_code, 429)
        content = response.content.decode()
        self.assertIn('Límite de Solicitudes Excedido', content)
        self.assertIn('Ha excedido el límite de solicitudes permitidas', content)
        self.assertIn('intente nuevamente en unos minutos', content)
    
    def test_rate_limit_template_has_back_link(self):
        """Test que verifica que la página de error tiene un enlace para volver"""
        url = reverse('certificates:query')
        
        # Exceder el límite
        for i in range(11):
            response = self.client.post(url, {'dni': '12345678'})
        
        # Verificar que hay un enlace para volver
        content = response.content.decode()
        self.assertIn('Volver a Consulta', content)
        self.assertIn(reverse('certificates:query'), content)
    
    def test_download_view_not_rate_limited(self):
        """Test que verifica que la vista de descarga no está limitada"""
        url = reverse('certificates:download', kwargs={'uuid': self.certificate.uuid})
        
        # Realizar 25 solicitudes (más que cualquier límite configurado)
        for i in range(25):
            response = self.client.get(url)
            # Puede ser 200 o 404 dependiendo de si el archivo existe
            self.assertIn(response.status_code, [200, 404], 
                         f"Download request {i+1} should not be rate limited")


class RateLimitMiddlewareTestCase(TestCase):
    """Tests para el middleware de rate limiting"""
    
    def setUp(self):
        """Configuración inicial para los tests"""
        # Limpiar cache antes de cada test
        cache.clear()
        
        self.event = Event.objects.create(
            name='Evento de Prueba',
            event_date=date(2024, 1, 15),
            description='Descripción del evento'
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
    
    def tearDown(self):
        """Limpieza después de cada test"""
        cache.clear()
    
    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    })
    def test_middleware_catches_ratelimited_exception(self):
        """Test que verifica que el middleware captura excepciones Ratelimited"""
        url = reverse('certificates:query')
        
        # Exceder el límite
        for i in range(11):
            response = self.client.post(url, {'dni': '87654321'})
        
        # Verificar que se retorna 429 y no 500
        self.assertEqual(response.status_code, 429)
        self.assertIn('Límite de Solicitudes Excedido', response.content.decode())
