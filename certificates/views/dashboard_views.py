"""Vistas del dashboard de estadísticas"""
import logging
import json
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.safestring import mark_safe

from certificates.services.dashboard_stats import DashboardStatsService
from certificates.models import Certificate

logger = logging.getLogger(__name__)


@staff_member_required
def dashboard_view(request):
    """
    Vista del dashboard de estadísticas.
    Solo accesible para usuarios staff.
    """
    try:
        service = DashboardStatsService()
        stats = service.get_dashboard_stats()
        
        # Obtener certificados recientes para la lista
        recent_certificates = Certificate.objects.select_related(
            'participant', 'participant__event'
        ).order_by('-generated_at')[:10]
        
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}", exc_info=True)
        messages.error(request, f"Error al cargar estadísticas: {e}")
        stats = {}
        recent_certificates = []
    
    # Serializar datos para JavaScript
    stats_json = stats.copy()
    if 'certificates' in stats_json and 'by_month' in stats_json['certificates']:
        stats_json['certificates']['by_month'] = mark_safe(json.dumps(stats_json['certificates']['by_month']))
    if 'queries' in stats_json and 'by_day' in stats_json['queries']:
        stats_json['queries']['by_day'] = mark_safe(json.dumps(stats_json['queries']['by_day']))
    
    context = {
        'stats': stats_json,
        'recent_certificates': recent_certificates,
        'last_updated': cache.get('dashboard_stats_timestamp'),
        'title': 'Dashboard de Estadísticas',
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
@require_http_methods(["POST"])
def dashboard_refresh(request):
    """
    Limpia el caché del dashboard y recalcula las estadísticas.
    """
    try:
        service = DashboardStatsService()
        service.clear_cache()
        
        # Recalcular estadísticas
        service.get_dashboard_stats()
        
        messages.success(request, "✓ Estadísticas actualizadas correctamente")
        
    except Exception as e:
        logger.error(f"Error refreshing dashboard: {e}", exc_info=True)
        messages.error(request, f"Error al actualizar estadísticas: {e}")
    
    # Redirigir de vuelta al dashboard
    from django.shortcuts import redirect
    return redirect('certificates:admin_dashboard')


# ============================================================================
# VISTAS LEGACY (mantener por compatibilidad)
# ============================================================================

from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from certificates.models import Event, Participant, Certificate, AuditLog


@method_decorator(staff_member_required, name="dispatch")
class DashboardChartsAPIView(TemplateView):
    """API para datos de gráficos del dashboard"""
    
    def get(self, request, *args, **kwargs):
        chart_type = request.GET.get('chart', 'certificates_by_month')
        
        if chart_type == 'certificates_by_month':
            return self.certificates_by_month()
        elif chart_type == 'events_by_month':
            return self.events_by_month()
        elif chart_type == 'verifications_by_day':
            return self.verifications_by_day()
        elif chart_type == 'attendee_types':
            return self.attendee_types_distribution()
        elif chart_type == 'signature_status':
            return self.signature_status()
        
        return JsonResponse({'error': 'Chart type not found'}, status=404)
    
    def certificates_by_month(self):
        """Certificados generados por mes (últimos 12 meses)"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=365)
        
        # Generar datos por mes
        months = []
        certificates_data = []
        
        current_date = start_date.replace(day=1)
        while current_date <= end_date:
            next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            
            count = Certificate.objects.filter(
                generated_at__gte=current_date,
                generated_at__lt=next_month
            ).count()
            
            months.append(current_date.strftime('%b %Y'))
            certificates_data.append(count)
            
            current_date = next_month
        
        return JsonResponse({
            'labels': months,
            'datasets': [{
                'label': 'Certificados Generados',
                'data': certificates_data,
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 2,
                'fill': True
            }]
        })
    
    def events_by_month(self):
        """Eventos creados por mes (últimos 12 meses)"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=365)
        
        months = []
        events_data = []
        
        current_date = start_date.replace(day=1)
        while current_date <= end_date:
            next_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            
            count = Event.objects.filter(
                created_at__gte=current_date,
                created_at__lt=next_month
            ).count()
            
            months.append(current_date.strftime('%b %Y'))
            events_data.append(count)
            
            current_date = next_month
        
        return JsonResponse({
            'labels': months,
            'datasets': [{
                'label': 'Eventos Creados',
                'data': events_data,
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 2,
                'fill': True
            }]
        })
    
    def verifications_by_day(self):
        """Verificaciones de certificados por día (últimos 30 días)"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        days = []
        verifications_data = []
        
        current_date = start_date
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            count = AuditLog.objects.filter(
                action_type='VERIFY',
                timestamp__date=current_date
            ).count()
            
            days.append(current_date.strftime('%d/%m'))
            verifications_data.append(count)
            
            current_date = next_date
        
        return JsonResponse({
            'labels': days,
            'datasets': [{
                'label': 'Verificaciones',
                'data': verifications_data,
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 2,
                'fill': True
            }]
        })
    
    def attendee_types_distribution(self):
        """Distribución por tipo de asistente"""
        stats = Participant.objects.values('attendee_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        labels = []
        data = []
        colors = [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 205, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
        ]
        
        for i, stat in enumerate(stats):
            type_display = {
                'ASISTENTE': 'Asistentes',
                'PONENTE': 'Ponentes',
                'ORGANIZADOR': 'Organizadores'
            }.get(stat['attendee_type'], stat['attendee_type'])
            
            labels.append(type_display)
            data.append(stat['count'])
        
        return JsonResponse({
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': colors[:len(data)],
                'borderWidth': 2
            }]
        })
    
    def signature_status(self):
        """Estado de firma de certificados"""
        signed = Certificate.objects.filter(is_signed=True).count()
        unsigned = Certificate.objects.filter(is_signed=False).count()
        
        return JsonResponse({
            'labels': ['Firmados Digitalmente', 'Sin Firma'],
            'datasets': [{
                'data': [signed, unsigned],
                'backgroundColor': [
                    'rgba(40, 167, 69, 0.8)',
                    'rgba(220, 53, 69, 0.8)'
                ],
                'borderWidth': 2
            }]
        })


@method_decorator(staff_member_required, name="dispatch")
class DashboardStatsAPIView(TemplateView):
    """API para estadísticas específicas del dashboard"""
    
    def get(self, request, *args, **kwargs):
        stat_type = request.GET.get('stat', 'overview')
        
        if stat_type == 'overview':
            return self.overview_stats()
        elif stat_type == 'performance':
            return self.performance_stats()
        elif stat_type == 'activity':
            return self.activity_stats()
        
        return JsonResponse({'error': 'Stat type not found'}, status=404)
    
    def overview_stats(self):
        """Estadísticas generales del sistema"""
        now = timezone.now()
        last_month = now - timedelta(days=30)
        last_week = now - timedelta(days=7)
        
        # Cálculos básicos
        total_certificates = Certificate.objects.count()
        certificates_last_month = Certificate.objects.filter(generated_at__gte=last_month).count()
        certificates_last_week = Certificate.objects.filter(generated_at__gte=last_week).count()
        
        # Cálculo de tendencias (comparar con período anterior)
        prev_month = last_month - timedelta(days=30)
        certificates_prev_month = Certificate.objects.filter(
            generated_at__gte=prev_month,
            generated_at__lt=last_month
        ).count()
        
        # Calcular porcentaje de cambio
        if certificates_prev_month > 0:
            cert_trend = ((certificates_last_month - certificates_prev_month) / certificates_prev_month) * 100
        else:
            cert_trend = 100 if certificates_last_month > 0 else 0
        
        return JsonResponse({
            'total_certificates': total_certificates,
            'certificates_last_month': certificates_last_month,
            'certificates_last_week': certificates_last_week,
            'certificate_trend': round(cert_trend, 1),
            'signature_rate': round((Certificate.objects.filter(is_signed=True).count() / max(total_certificates, 1)) * 100, 1),
            'avg_certificates_per_event': round(total_certificates / max(Event.objects.count(), 1), 1)
        })
    
    def performance_stats(self):
        """Estadísticas de performance del sistema"""
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        
        # Actividad en las últimas 24 horas
        recent_activity = {
            'imports': AuditLog.objects.filter(
                action_type='IMPORT',
                timestamp__gte=last_24h
            ).count(),
            'generations': AuditLog.objects.filter(
                action_type='GENERATE',
                timestamp__gte=last_24h
            ).count(),
            'signatures': AuditLog.objects.filter(
                action_type='SIGN',
                timestamp__gte=last_24h
            ).count(),
            'verifications': AuditLog.objects.filter(
                action_type='VERIFY',
                timestamp__gte=last_24h
            ).count(),
        }
        
        # Eventos más populares (por número de participantes)
        popular_events = Event.objects.annotate(
            participant_count=Count('participants')
        ).order_by('-participant_count')[:5]
        
        popular_events_data = [{
            'name': event.name,
            'participants': event.participant_count,
            'date': event.event_date.strftime('%d/%m/%Y')
        } for event in popular_events]
        
        return JsonResponse({
            'recent_activity': recent_activity,
            'popular_events': popular_events_data,
            'total_activity_24h': sum(recent_activity.values())
        })
    
    def activity_stats(self):
        """Estadísticas de actividad por hora del día"""
        # Actividad por hora en los últimos 7 días
        last_week = timezone.now() - timedelta(days=7)
        
        hourly_activity = {}
        for hour in range(24):
            hourly_activity[hour] = AuditLog.objects.filter(
                timestamp__gte=last_week,
                timestamp__hour=hour
            ).count()
        
        return JsonResponse({
            'hourly_activity': hourly_activity,
            'peak_hour': max(hourly_activity, key=hourly_activity.get),
            'total_activity_week': sum(hourly_activity.values())
        })