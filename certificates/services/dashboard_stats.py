"""
Servicio para calcular estadísticas del dashboard de administración.
"""
import logging
import time
from datetime import timedelta
from django.core.cache import cache
from django.db.models import Count, Q, Avg
from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone

from certificates.models import Certificate, AuditLog, CertificateTemplate, Event, Participant

logger = logging.getLogger(__name__)


class DashboardStatsService:
    """Servicio para calcular estadísticas del dashboard"""
    
    CACHE_KEY = 'dashboard_stats'
    CACHE_TTL = 300  # 5 minutos
    
    def get_dashboard_stats(self) -> dict:
        """
        Obtiene todas las estadísticas del dashboard.
        Usa caché para optimizar rendimiento.
        
        Returns:
            dict: Diccionario con todas las estadísticas
        """
        start_time = time.time()
        
        try:
            # Intentar obtener del caché
            cached_stats = cache.get(self.CACHE_KEY)
            if cached_stats:
                logger.info("Dashboard stats loaded from cache")
                return cached_stats
            
            # Calcular estadísticas
            logger.info("Calculating dashboard stats...")
            stats = self._calculate_all_stats()
            
            # Guardar en caché
            cache.set(self.CACHE_KEY, stats, self.CACHE_TTL)
            cache.set(f'{self.CACHE_KEY}_timestamp', timezone.now(), self.CACHE_TTL)
            
            elapsed = time.time() - start_time
            logger.info(f"Dashboard stats calculated in {elapsed:.2f}s")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating dashboard stats: {e}", exc_info=True)
            # Retornar estadísticas vacías en caso de error
            return self._get_empty_stats()
    
    def _calculate_all_stats(self) -> dict:
        """Calcula todas las estadísticas del dashboard"""
        return {
            'certificates': self._calculate_certificate_stats(),
            'queries': self._calculate_query_stats(),
            'templates': self._calculate_template_stats(),
            'quick_stats': self._calculate_quick_stats(),
        }
    
    def _calculate_certificate_stats(self) -> dict:
        """
        Calcula estadísticas de certificados.
        
        Returns:
            dict: Estadísticas de certificados
        """
        # Agregaciones en una sola query
        cert_aggregates = Certificate.objects.aggregate(
            total=Count('id'),
            signed=Count('id', filter=Q(is_signed=True)),
            unsigned=Count('id', filter=Q(is_signed=False)),
            internal=Count('id', filter=Q(is_external=False)),
            external=Count('id', filter=Q(is_external=True))
        )
        
        # Certificados por mes (últimos 6 meses)
        by_month = self._get_certificates_by_month(months=6)
        
        return {
            'total': cert_aggregates['total'] or 0,
            'signed': cert_aggregates['signed'] or 0,
            'unsigned': cert_aggregates['unsigned'] or 0,
            'internal': cert_aggregates['internal'] or 0,
            'external': cert_aggregates['external'] or 0,
            'by_month': by_month,
        }

    def _calculate_query_stats(self) -> dict:
        """
        Calcula estadísticas de consultas.
        
        Returns:
            dict: Estadísticas de consultas
        """
        # Total de consultas
        total_queries = AuditLog.objects.filter(action_type='QUERY').count()
        
        # Consultas de hoy
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_queries = AuditLog.objects.filter(
            action_type='QUERY',
            timestamp__gte=today_start
        ).count()
        
        # Consultas por día (últimos 7 días)
        by_day = self._get_queries_by_day(days=7)
        
        return {
            'total': total_queries,
            'today': today_queries,
            'by_day': by_day,
        }
    
    def _calculate_template_stats(self) -> dict:
        """
        Calcula estadísticas de plantillas.
        
        Returns:
            dict: Estadísticas de plantillas
        """
        # Total de plantillas
        total_templates = CertificateTemplate.objects.count()
        
        # Plantilla más usada
        most_used = CertificateTemplate.objects.annotate(
            usage_count=Count('event__participants__certificate')
        ).order_by('-usage_count').first()
        
        most_used_data = None
        if most_used:
            most_used_data = {
                'name': most_used.name,
                'usage_count': most_used.usage_count
            }
        
        # Últimas 5 plantillas creadas
        recent_templates = CertificateTemplate.objects.order_by('-created_at')[:5]
        recent = [
            {
                'name': template.name,
                'created_at': template.created_at.strftime('%d/%m/%Y')
            }
            for template in recent_templates
        ]
        
        return {
            'total': total_templates,
            'most_used': most_used_data,
            'recent': recent,
        }
    
    def _calculate_quick_stats(self) -> dict:
        """
        Calcula estadísticas rápidas adicionales.
        
        Returns:
            dict: Estadísticas rápidas
        """
        events_count = Event.objects.count()
        participants_count = Participant.objects.count()
        
        # Promedio de certificados por evento
        avg_certs = 0
        if events_count > 0:
            avg_certs = Certificate.objects.count() / events_count
        
        return {
            'events_count': events_count,
            'participants_count': participants_count,
            'avg_certificates_per_event': round(avg_certs, 1),
        }
    
    def _get_certificates_by_month(self, months: int = 6) -> list:
        """
        Obtiene certificados agrupados por mes.
        
        Args:
            months: Número de meses a consultar
            
        Returns:
            list: Lista de diccionarios con mes y conteo
        """
        months_ago = timezone.now() - timedelta(days=months * 30)
        
        certs_by_month = Certificate.objects.filter(
            generated_at__gte=months_ago
        ).annotate(
            month=TruncMonth('generated_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Formatear resultados
        result = []
        for item in certs_by_month:
            if item['month']:
                result.append({
                    'month': item['month'].strftime('%Y-%m'),
                    'month_label': item['month'].strftime('%b %Y'),
                    'count': item['count']
                })
        
        return result
    
    def _get_queries_by_day(self, days: int = 7) -> list:
        """
        Obtiene consultas agrupadas por día.
        
        Args:
            days: Número de días a consultar
            
        Returns:
            list: Lista de diccionarios con fecha y conteo
        """
        days_ago = timezone.now() - timedelta(days=days)
        
        queries_by_day = AuditLog.objects.filter(
            action_type='QUERY',
            timestamp__gte=days_ago
        ).annotate(
            date=TruncDate('timestamp')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Formatear resultados
        result = []
        for item in queries_by_day:
            if item['date']:
                result.append({
                    'date': item['date'].strftime('%Y-%m-%d'),
                    'date_label': item['date'].strftime('%d/%m'),
                    'count': item['count']
                })
        
        return result
    
    def _get_empty_stats(self) -> dict:
        """
        Retorna estructura de estadísticas vacía.
        
        Returns:
            dict: Estadísticas vacías
        """
        return {
            'certificates': {
                'total': 0,
                'signed': 0,
                'unsigned': 0,
                'internal': 0,
                'external': 0,
                'by_month': [],
            },
            'queries': {
                'total': 0,
                'today': 0,
                'by_day': [],
            },
            'templates': {
                'total': 0,
                'most_used': None,
                'recent': [],
            },
            'quick_stats': {
                'events_count': 0,
                'participants_count': 0,
                'avg_certificates_per_event': 0,
            }
        }
    
    def clear_cache(self):
        """Limpia el caché de estadísticas"""
        cache.delete(self.CACHE_KEY)
        cache.delete(f'{self.CACHE_KEY}_timestamp')
        logger.info("Dashboard stats cache cleared")
