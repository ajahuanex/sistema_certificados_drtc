# Design Document

## Overview

El dashboard de estadísticas proporcionará una vista centralizada y visual de las métricas clave del sistema de certificados DRTC. Se integrará en el panel de administración de Django, utilizando el sistema de templates existente y agregando nuevas vistas, servicios y componentes visuales.

El diseño se enfoca en:
- Reutilizar la infraestructura existente (modelos, admin, templates)
- Crear un servicio de estadísticas con caché para optimizar rendimiento
- Diseño responsive con cards y gráficos usando Chart.js
- Integración fluida con el admin de Django

## Architecture

### Componentes Principales

```
┌─────────────────────────────────────────────────────────┐
│                    Admin Dashboard View                  │
│  (certificates/views/dashboard_views.py)                │
└────────────────┬────────────────────────────────────────┘
                 │
                 ├──> DashboardStatsService
                 │    (certificates/services/dashboard_stats.py)
                 │    - Calcula estadísticas
                 │    - Implementa caché
                 │    - Agrupa queries
                 │
                 ├──> Models (Certificate, AuditLog, etc.)
                 │    - Queries optimizadas
                 │    - Agregaciones
                 │
                 └──> Template (templates/admin/dashboard.html)
                      - Cards de estadísticas
                      - Gráficos Chart.js
                      - Acciones rápidas
```

### Flujo de Datos

1. Usuario accede a `/admin/dashboard/`
2. Vista llama a `DashboardStatsService.get_dashboard_stats()`
3. Servicio verifica caché (5 minutos TTL)
4. Si no hay caché, ejecuta queries optimizadas
5. Guarda resultado en caché
6. Retorna datos al template
7. Template renderiza cards y gráficos con Chart.js

## Components and Interfaces

### 1. DashboardStatsService

Servicio centralizado para calcular todas las estadísticas del dashboard.

```python
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
        
    def _calculate_certificate_stats(self) -> dict:
        """Calcula estadísticas de certificados"""
        
    def _calculate_query_stats(self) -> dict:
        """Calcula estadísticas de consultas"""
        
    def _calculate_template_stats(self) -> dict:
        """Calcula estadísticas de plantillas"""
        
    def _get_certificates_by_month(self, months: int = 6) -> list:
        """Obtiene certificados agrupados por mes"""
        
    def _get_queries_by_day(self, days: int = 7) -> list:
        """Obtiene consultas agrupadas por día"""
        
    def clear_cache(self):
        """Limpia el caché de estadísticas"""
```

### 2. Dashboard View

Vista de Django que renderiza el dashboard.

```python
@staff_member_required
def dashboard_view(request):
    """
    Vista del dashboard de estadísticas.
    Solo accesible para usuarios staff.
    """
    service = DashboardStatsService()
    stats = service.get_dashboard_stats()
    
    context = {
        'stats': stats,
        'last_updated': cache.get('dashboard_stats_timestamp'),
    }
    
    return render(request, 'admin/dashboard.html', context)
```

### 3. URL Configuration

Agregar ruta al dashboard en el admin.

```python
# En certificates/urls.py o config/urls.py
urlpatterns = [
    path('admin/dashboard/', dashboard_view, name='admin_dashboard'),
    # ... otras rutas
]
```

### 4. Template Structure

```html
<!-- templates/admin/dashboard.html -->
{% extends "admin/base_site.html" %}
{% load static %}

{% block extrastyle %}
    <link rel="stylesheet" href="{% static 'admin/css/dashboard.css' %}">
{% endblock %}

{% block content %}
<div class="dashboard-container">
    <!-- Header -->
    <div class="dashboard-header">
        <h1>📊 Dashboard de Estadísticas</h1>
        <p class="last-updated">Última actualización: {{ last_updated }}</p>
    </div>
    
    <!-- Stats Cards -->
    <div class="stats-grid">
        <!-- Certificados Totales -->
        <div class="stat-card">...</div>
        
        <!-- Certificados Firmados -->
        <div class="stat-card">...</div>
        
        <!-- Consultas Hoy -->
        <div class="stat-card">...</div>
        
        <!-- Plantillas Activas -->
        <div class="stat-card">...</div>
    </div>
    
    <!-- Charts -->
    <div class="charts-grid">
        <!-- Gráfico de Certificados por Mes -->
        <div class="chart-card">
            <canvas id="certificatesChart"></canvas>
        </div>
        
        <!-- Gráfico de Consultas por Día -->
        <div class="chart-card">
            <canvas id="queriesChart"></canvas>
        </div>
    </div>
    
    <!-- Quick Actions -->
    <div class="quick-actions">...</div>
    
    <!-- Recent Certificates -->
    <div class="recent-list">...</div>
</div>
{% endblock %}

{% block extrajs %}
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="{% static 'admin/js/dashboard.js' %}"></script>
{% endblock %}
```

## Data Models

### Estadísticas Calculadas

El servicio retornará un diccionario con la siguiente estructura:

```python
{
    'certificates': {
        'total': 1250,
        'signed': 980,
        'unsigned': 270,
        'internal': 1100,
        'external': 150,
        'by_month': [
            {'month': '2024-05', 'count': 120},
            {'month': '2024-06', 'count': 180},
            # ... últimos 6 meses
        ]
    },
    'queries': {
        'total': 5420,
        'today': 45,
        'by_day': [
            {'date': '2024-10-25', 'count': 52},
            {'date': '2024-10-26', 'count': 48},
            # ... últimos 7 días
        ]
    },
    'templates': {
        'total': 8,
        'most_used': {
            'name': 'Certificado Estándar',
            'usage_count': 850
        },
        'recent': [
            {'name': 'Plantilla Nueva', 'created_at': '2024-10-20'},
            # ... últimas 5
        ]
    },
    'quick_stats': {
        'events_count': 45,
        'participants_count': 1250,
        'avg_certificates_per_event': 27.8
    }
}
```

### Queries Optimizadas

Para evitar N+1 queries y mejorar rendimiento:

```python
# Certificados con agregaciones
Certificate.objects.aggregate(
    total=Count('id'),
    signed=Count('id', filter=Q(is_signed=True)),
    internal=Count('id', filter=Q(is_external=False)),
    external=Count('id', filter=Q(is_external=True))
)

# Certificados por mes (últimos 6 meses)
Certificate.objects.filter(
    generated_at__gte=six_months_ago
).annotate(
    month=TruncMonth('generated_at')
).values('month').annotate(
    count=Count('id')
).order_by('month')

# Consultas por día (últimos 7 días)
AuditLog.objects.filter(
    action_type='QUERY',
    timestamp__gte=seven_days_ago
).annotate(
    date=TruncDate('timestamp')
).values('date').annotate(
    count=Count('id')
).order_by('date')

# Plantilla más usada
CertificateTemplate.objects.annotate(
    usage_count=Count('event__participants__certificate')
).order_by('-usage_count').first()
```

## Error Handling

### Manejo de Errores en el Servicio

```python
def get_dashboard_stats(self) -> dict:
    try:
        # Intentar obtener del caché
        cached_stats = cache.get(self.CACHE_KEY)
        if cached_stats:
            return cached_stats
        
        # Calcular estadísticas
        stats = self._calculate_all_stats()
        
        # Guardar en caché
        cache.set(self.CACHE_KEY, stats, self.CACHE_TTL)
        cache.set(f'{self.CACHE_KEY}_timestamp', timezone.now(), self.CACHE_TTL)
        
        return stats
        
    except Exception as e:
        logger.error(f"Error calculating dashboard stats: {e}")
        # Retornar estadísticas vacías en caso de error
        return self._get_empty_stats()
```

### Manejo de Errores en la Vista

```python
def dashboard_view(request):
    try:
        service = DashboardStatsService()
        stats = service.get_dashboard_stats()
        
    except Exception as e:
        messages.error(request, f"Error al cargar estadísticas: {e}")
        stats = {}
    
    context = {
        'stats': stats,
        'last_updated': cache.get('dashboard_stats_timestamp'),
    }
    
    return render(request, 'admin/dashboard.html', context)
```

## Testing Strategy

### Unit Tests

```python
class DashboardStatsServiceTest(TestCase):
    """Tests para el servicio de estadísticas"""
    
    def setUp(self):
        # Crear datos de prueba
        self.service = DashboardStatsService()
        
    def test_calculate_certificate_stats(self):
        """Verifica cálculo de estadísticas de certificados"""
        
    def test_calculate_query_stats(self):
        """Verifica cálculo de estadísticas de consultas"""
        
    def test_cache_functionality(self):
        """Verifica que el caché funciona correctamente"""
        
    def test_empty_database(self):
        """Verifica comportamiento con base de datos vacía"""
```

### Integration Tests

```python
class DashboardViewTest(TestCase):
    """Tests para la vista del dashboard"""
    
    def test_dashboard_requires_authentication(self):
        """Verifica que requiere autenticación"""
        
    def test_dashboard_displays_stats(self):
        """Verifica que muestra estadísticas correctamente"""
        
    def test_dashboard_handles_errors(self):
        """Verifica manejo de errores"""
```

### Performance Tests

```python
class DashboardPerformanceTest(TestCase):
    """Tests de rendimiento del dashboard"""
    
    def test_dashboard_loads_under_2_seconds(self):
        """Verifica que carga en menos de 2 segundos"""
        
    def test_cache_improves_performance(self):
        """Verifica que el caché mejora el rendimiento"""
```

## UI/UX Design

### Color Scheme

```css
:root {
    --primary-color: #007cba;
    --success-color: #2e7d32;
    --warning-color: #f57c00;
    --danger-color: #c62828;
    --info-color: #6a1b9a;
    --card-bg: #ffffff;
    --card-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
```

### Card Design

```css
.stat-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 24px;
    box-shadow: var(--card-shadow);
    transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0,0,0,0.15);
}

.stat-card .icon {
    font-size: 48px;
    margin-bottom: 12px;
}

.stat-card .value {
    font-size: 36px;
    font-weight: bold;
    color: var(--primary-color);
}

.stat-card .label {
    font-size: 14px;
    color: #666;
    text-transform: uppercase;
}
```

### Responsive Grid

```css
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

@media (max-width: 768px) {
    .charts-grid {
        grid-template-columns: 1fr;
    }
}
```

### Chart Configuration

```javascript
// Configuración de Chart.js para gráfico de certificados
const certificatesChartConfig = {
    type: 'bar',
    data: {
        labels: monthLabels,
        datasets: [{
            label: 'Certificados Generados',
            data: monthData,
            backgroundColor: 'rgba(0, 124, 186, 0.7)',
            borderColor: 'rgba(0, 124, 186, 1)',
            borderWidth: 2
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top'
            },
            title: {
                display: true,
                text: 'Certificados por Mes (Últimos 6 meses)'
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    stepSize: 1
                }
            }
        }
    }
};
```

## Integration Points

### 1. Admin Index Integration

Modificar `templates/admin/index.html` para agregar enlace al dashboard:

```html
<!-- Agregar al inicio del bloque content -->
<div class="dashboard-link-card">
    <a href="{% url 'admin_dashboard' %}" class="dashboard-button">
        📊 Ver Dashboard de Estadísticas
    </a>
</div>
```

### 2. Admin Site Configuration

Registrar el dashboard en el admin site:

```python
# En certificates/admin.py
from django.contrib import admin
from django.urls import path

class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(dashboard_view), name='admin_dashboard'),
        ]
        return custom_urls + urls
```

### 3. Context Processor (Opcional)

Para hacer el dashboard disponible en todos los templates del admin:

```python
# En config/settings/base.py
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ... otros processors
                'certificates.context_processors.dashboard_context',
            ],
        },
    },
]

# En certificates/context_processors.py
def dashboard_context(request):
    if request.user.is_staff:
        return {
            'dashboard_url': reverse('admin_dashboard')
        }
    return {}
```

## Performance Optimization

### Caché Strategy

1. **Caché de estadísticas completas**: 5 minutos TTL
2. **Invalidación manual**: Botón "Actualizar" en el dashboard
3. **Caché por usuario**: No necesario (mismas stats para todos los admins)

### Query Optimization

1. Usar `select_related()` y `prefetch_related()` donde sea necesario
2. Agregar índices en campos usados para filtrado:
   - `Certificate.generated_at`
   - `AuditLog.timestamp`
   - `AuditLog.action_type`
3. Usar agregaciones de base de datos en lugar de Python

### Frontend Optimization

1. Cargar Chart.js desde CDN con caché
2. Lazy loading de gráficos (solo cuando son visibles)
3. Minimizar CSS y JS en producción

## Security Considerations

1. **Autenticación**: Solo usuarios `is_staff=True` pueden acceder
2. **Autorización**: Verificar permisos en la vista
3. **Rate Limiting**: Limitar requests al dashboard (opcional)
4. **SQL Injection**: Usar ORM de Django (protección automática)
5. **XSS**: Escapar datos en templates (Django lo hace por defecto)

## Deployment Considerations

### Static Files

```bash
# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

### Cache Backend

En producción, usar Redis o Memcached:

```python
# config/settings/production.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Monitoring

Agregar logging para monitorear rendimiento:

```python
import logging
logger = logging.getLogger(__name__)

def get_dashboard_stats(self):
    start_time = time.time()
    # ... cálculos
    elapsed = time.time() - start_time
    logger.info(f"Dashboard stats calculated in {elapsed:.2f}s")
```
