"""
Tests para el servicio de estadísticas del dashboard.
"""
from django.test import TestCase
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta

from certificates.services.dashboard_stats import DashboardStatsService
from certificates.models import (
    Certificate, AuditLog, CertificateTemplate, Event, Participant
)


class DashboardStatsServiceTest(TestCase):
    """Tests para el servicio de estadísticas del dashboard"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.service = DashboardStatsService()
        cache.clear()
        
        # Crear datos de prueba
        self.template = CertificateTemplate.objects.create(
            name="Plantilla Test",
            html_template="<html>Test</html>"
        )
        
        self.event = Event.objects.create(
            name="Evento Test",
            event_date=timezone.now().date(),
            template=self.template
        )
        
        self.participant = Participant.objects.create(
            dni="12345678",
            full_name="Juan Pérez",
            event=self.event,
            attendee_type="ASISTENTE"
        )
    
    def tearDown(self):
        """Limpieza después de cada test"""
        cache.clear()
    
    def test_get_dashboard_stats_structure(self):
        """Verifica que get_dashboard_stats retorna la estructura correcta"""
        stats = self.service.get_dashboard_stats()
        
        # Verificar estructura principal
        self.assertIn('certificates', stats)
        self.assertIn('queries', stats)
        self.assertIn('templates', stats)
        self.assertIn('quick_stats', stats)
        
        # Verificar estructura de certificates
        self.assertIn('total', stats['certificates'])
        self.assertIn('signed', stats['certificates'])
        self.assertIn('unsigned', stats['certificates'])
        self.assertIn('internal', stats['certificates'])
        self.assertIn('external', stats['certificates'])
        self.assertIn('by_month', stats['certificates'])
        
        # Verificar estructura de queries
        self.assertIn('total', stats['queries'])
        self.assertIn('today', stats['queries'])
        self.assertIn('by_day', stats['queries'])
        
        # Verificar estructura de templates
        self.assertIn('total', stats['templates'])
        self.assertIn('most_used', stats['templates'])
        self.assertIn('recent', stats['templates'])
    
    def test_calculate_certificate_stats_empty(self):
        """Verifica cálculo de estadísticas con base de datos vacía"""
        stats = self.service._calculate_certificate_stats()
        
        self.assertEqual(stats['total'], 0)
        self.assertEqual(stats['signed'], 0)
        self.assertEqual(stats['unsigned'], 0)
        self.assertEqual(stats['internal'], 0)
        self.assertEqual(stats['external'], 0)
        self.assertEqual(len(stats['by_month']), 0)
    
    def test_calculate_certificate_stats_with_data(self):
        """Verifica cálculo de estadísticas con certificados"""
        # Crear certificados de prueba
        cert1 = Certificate.objects.create(
            participant=self.participant,
            is_signed=True,
            is_external=False
        )
        
        participant2 = Participant.objects.create(
            dni="87654321",
            full_name="María García",
            event=self.event,
            attendee_type="PONENTE"
        )
        cert2 = Certificate.objects.create(
            participant=participant2,
            is_signed=False,
            is_external=True
        )
        
        stats = self.service._calculate_certificate_stats()
        
        self.assertEqual(stats['total'], 2)
        self.assertEqual(stats['signed'], 1)
        self.assertEqual(stats['unsigned'], 1)
        self.assertEqual(stats['internal'], 1)
        self.assertEqual(stats['external'], 1)
    
    def test_calculate_query_stats_empty(self):
        """Verifica cálculo de estadísticas de consultas vacías"""
        stats = self.service._calculate_query_stats()
        
        self.assertEqual(stats['total'], 0)
        self.assertEqual(stats['today'], 0)
        self.assertEqual(len(stats['by_day']), 0)
    
    def test_calculate_query_stats_with_data(self):
        """Verifica cálculo de estadísticas con consultas"""
        # Crear logs de consulta
        AuditLog.objects.create(
            action_type='QUERY',
            description='Consulta de prueba 1'
        )
        AuditLog.objects.create(
            action_type='QUERY',
            description='Consulta de prueba 2'
        )
        AuditLog.objects.create(
            action_type='GENERATE',  # No es QUERY
            description='Generación de prueba'
        )
        
        stats = self.service._calculate_query_stats()
        
        self.assertEqual(stats['total'], 2)
        self.assertEqual(stats['today'], 2)
    
    def test_calculate_template_stats(self):
        """Verifica cálculo de estadísticas de plantillas"""
        # Crear más plantillas
        CertificateTemplate.objects.create(
            name="Plantilla 2",
            html_template="<html>Test 2</html>"
        )
        
        stats = self.service._calculate_template_stats()
        
        self.assertEqual(stats['total'], 2)
        self.assertIsInstance(stats['recent'], list)
        self.assertLessEqual(len(stats['recent']), 5)
    
    def test_calculate_quick_stats(self):
        """Verifica cálculo de estadísticas rápidas"""
        stats = self.service._calculate_quick_stats()
        
        self.assertEqual(stats['events_count'], 1)
        self.assertEqual(stats['participants_count'], 1)
        self.assertIsInstance(stats['avg_certificates_per_event'], float)
    
    def test_cache_functionality(self):
        """Verifica que el caché funciona correctamente"""
        # Primera llamada - debe calcular
        stats1 = self.service.get_dashboard_stats()
        
        # Crear nuevo certificado
        Certificate.objects.create(
            participant=self.participant,
            is_signed=True
        )
        
        # Segunda llamada - debe usar caché (no reflejar el nuevo certificado)
        stats2 = self.service.get_dashboard_stats()
        
        self.assertEqual(stats1['certificates']['total'], stats2['certificates']['total'])
        
        # Limpiar caché
        self.service.clear_cache()
        
        # Tercera llamada - debe recalcular
        stats3 = self.service.get_dashboard_stats()
        
        self.assertNotEqual(stats1['certificates']['total'], stats3['certificates']['total'])
    
    def test_get_certificates_by_month(self):
        """Verifica obtención de certificados por mes"""
        # Crear certificado
        Certificate.objects.create(
            participant=self.participant,
            is_signed=True
        )
        
        by_month = self.service._get_certificates_by_month(months=6)
        
        self.assertIsInstance(by_month, list)
        if len(by_month) > 0:
            self.assertIn('month', by_month[0])
            self.assertIn('month_label', by_month[0])
            self.assertIn('count', by_month[0])
    
    def test_get_queries_by_day(self):
        """Verifica obtención de consultas por día"""
        # Crear consultas
        AuditLog.objects.create(
            action_type='QUERY',
            description='Consulta test'
        )
        
        by_day = self.service._get_queries_by_day(days=7)
        
        self.assertIsInstance(by_day, list)
        if len(by_day) > 0:
            self.assertIn('date', by_day[0])
            self.assertIn('date_label', by_day[0])
            self.assertIn('count', by_day[0])
    
    def test_empty_stats_structure(self):
        """Verifica estructura de estadísticas vacías"""
        empty_stats = self.service._get_empty_stats()
        
        self.assertEqual(empty_stats['certificates']['total'], 0)
        self.assertEqual(empty_stats['queries']['total'], 0)
        self.assertEqual(empty_stats['templates']['total'], 0)
        self.assertEqual(empty_stats['quick_stats']['events_count'], 0)
    
    def test_error_handling(self):
        """Verifica manejo de errores en el servicio"""
        # Simular error forzando una excepción
        original_method = self.service._calculate_all_stats
        
        def mock_error():
            raise Exception("Error simulado")
        
        self.service._calculate_all_stats = mock_error
        
        # Debe retornar estadísticas vacías sin lanzar excepción
        stats = self.service.get_dashboard_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['certificates']['total'], 0)
        
        # Restaurar método original
        self.service._calculate_all_stats = original_method
    
    def test_template_most_used_with_certificates(self):
        """Verifica cálculo de plantilla más usada"""
        # Crear certificados con la plantilla
        for i in range(3):
            participant = Participant.objects.create(
                dni=f"1234567{i}",
                full_name=f"Participante {i}",
                event=self.event,
                attendee_type="ASISTENTE"
            )
            Certificate.objects.create(
                participant=participant,
                is_signed=True
            )
        
        stats = self.service._calculate_template_stats()
        
        self.assertIsNotNone(stats['most_used'])
        self.assertEqual(stats['most_used']['name'], "Plantilla Test")
        self.assertEqual(stats['most_used']['usage_count'], 3)
    
    def test_cache_ttl(self):
        """Verifica que el TTL del caché está configurado"""
        self.assertEqual(self.service.CACHE_TTL, 300)
        self.assertEqual(self.service.CACHE_KEY, 'dashboard_stats')
    
    def test_clear_cache(self):
        """Verifica que clear_cache limpia el caché correctamente"""
        # Guardar algo en caché
        self.service.get_dashboard_stats()
        
        # Verificar que está en caché
        cached = cache.get(self.service.CACHE_KEY)
        self.assertIsNotNone(cached)
        
        # Limpiar caché
        self.service.clear_cache()
        
        # Verificar que se limpió
        cached = cache.get(self.service.CACHE_KEY)
        self.assertIsNone(cached)
