# Dashboard de Estadísticas

## Descripción General

El Dashboard de Estadísticas proporciona una vista centralizada y visual de las métricas clave del sistema de certificados DRTC. Permite a los administradores monitorear el estado y uso del sistema de manera eficiente.

## Acceso al Dashboard

### URL
```
/admin/dashboard/
```

### Requisitos
- Usuario autenticado con permisos de staff (`is_staff=True`)
- Acceso al panel de administración de Django

### Desde el Admin
1. Inicia sesión en el panel de administración
2. En la página principal verás un card destacado "📊 Dashboard de Estadísticas"
3. Haz clic en "🚀 Ver Dashboard"

## Métricas Disponibles

### 1. Estadísticas Principales (Cards)

#### 📄 Certificados Totales
- **Descripción**: Número total de certificados generados en el sistema
- **Incluye**: Certificados internos y externos

#### ✓ Certificados Firmados
- **Descripción**: Número de certificados con firma digital
- **Detalle adicional**: Muestra también cuántos están sin firmar

#### 🔍 Consultas Hoy
- **Descripción**: Número de consultas de certificados realizadas en el día actual
- **Detalle adicional**: Muestra el total histórico de consultas

#### 📋 Plantillas Activas
- **Descripción**: Número total de plantillas de certificados disponibles

### 2. Estadísticas Secundarias

- **Certificados Internos**: Generados dentro del sistema
- **Certificados Externos**: Importados de otros sistemas
- **Total Eventos**: Eventos de capacitación registrados
- **Total Participantes**: Participantes registrados en todos los eventos
- **Promedio Cert/Evento**: Promedio de certificados por evento

### 3. Gráficos

#### 📈 Certificados por Mes
- **Tipo**: Gráfico de barras
- **Período**: Últimos 6 meses
- **Descripción**: Muestra la tendencia de generación de certificados
- **Uso**: Identificar períodos de mayor actividad

#### 📊 Consultas por Día
- **Tipo**: Gráfico de líneas
- **Período**: Última semana (7 días)
- **Descripción**: Muestra el patrón de consultas diarias
- **Uso**: Identificar días de mayor demanda

### 4. Acciones Rápidas

Botones de acceso directo a las funciones más utilizadas:

- **📥 Importar Excel**: Importar participantes desde archivo Excel
- **🔗 Importar Externos**: Importar certificados de sistemas externos
- **📄 Ver Certificados**: Ir al listado de certificados
- **📅 Ver Eventos**: Ir al listado de eventos

### 5. Certificados Recientes

Tabla con los últimos 10 certificados generados, mostrando:
- UUID (con enlace al detalle)
- Participante
- DNI
- Evento
- Tipo (Interno/Externo)
- Estado (Firmado/Sin firmar)
- Fecha de generación

### 6. Estadísticas de Plantillas

#### 🏆 Plantilla Más Usada
- Nombre de la plantilla
- Número de certificados generados con ella

#### 🆕 Plantillas Recientes
- Lista de las últimas 5 plantillas creadas
- Fecha de creación de cada una

## Actualización de Datos

### Caché Automático
- **Duración**: 5 minutos (300 segundos)
- **Propósito**: Optimizar el rendimiento y reducir carga en la base de datos
- **Comportamiento**: Las estadísticas se calculan una vez y se guardan en caché

### Actualización Manual
1. Haz clic en el botón "🔄 Actualizar" en la esquina superior derecha
2. El sistema limpiará el caché y recalculará todas las estadísticas
3. Verás un mensaje de confirmación
4. La fecha de "Última actualización" se actualizará

### Indicador de Actualización
En la parte superior del dashboard se muestra:
```
Última actualización: 31/10/2024 14:30:45
```

## Rendimiento

### Optimizaciones Implementadas

1. **Caché de Estadísticas**
   - TTL: 5 minutos
   - Backend: Configurado en settings (puede ser Redis en producción)

2. **Queries Optimizadas**
   - Uso de agregaciones de Django ORM
   - Queries agrupadas para reducir N+1
   - Índices en campos de filtrado

3. **Tiempo de Carga**
   - Primera carga (sin caché): < 2 segundos
   - Cargas subsecuentes (con caché): < 100ms

### Monitoreo
El sistema registra en logs:
- Tiempo de cálculo de estadísticas
- Uso de caché (hit/miss)
- Errores en el cálculo

## Configuración

### Caché Backend

#### Desarrollo (por defecto)
```python
# config/settings/base.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

#### Producción (recomendado)
```python
# config/settings/production.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Personalización del TTL

Para cambiar la duración del caché, edita:
```python
# certificates/services/dashboard_stats.py
class DashboardStatsService:
    CACHE_TTL = 300  # Cambiar a los segundos deseados
```

## Solución de Problemas

### El dashboard no carga
1. Verifica que el usuario tenga permisos de staff
2. Revisa los logs del servidor para errores
3. Verifica la conexión a la base de datos

### Las estadísticas parecen incorrectas
1. Haz clic en "🔄 Actualizar" para limpiar el caché
2. Verifica que los datos en la base de datos sean correctos
3. Revisa los logs para errores en el cálculo

### Los gráficos no se muestran
1. Verifica que Chart.js se cargue correctamente (revisa la consola del navegador)
2. Asegúrate de que los archivos estáticos estén servidos correctamente
3. Ejecuta `python manage.py collectstatic` en producción

### Error "dashboard_url not found"
1. Verifica que el context processor esté configurado en settings
2. Reinicia el servidor de Django
3. Verifica que el usuario esté autenticado

## API Interna

### Servicio de Estadísticas

```python
from certificates.services.dashboard_stats import DashboardStatsService

# Obtener estadísticas
service = DashboardStatsService()
stats = service.get_dashboard_stats()

# Limpiar caché
service.clear_cache()
```

### Estructura de Datos Retornada

```python
{
    'certificates': {
        'total': 1250,
        'signed': 980,
        'unsigned': 270,
        'internal': 1100,
        'external': 150,
        'by_month': [
            {'month': '2024-05', 'month_label': 'May 2024', 'count': 120},
            # ...
        ]
    },
    'queries': {
        'total': 5420,
        'today': 45,
        'by_day': [
            {'date': '2024-10-25', 'date_label': '25/10', 'count': 52},
            # ...
        ]
    },
    'templates': {
        'total': 8,
        'most_used': {
            'name': 'Certificado Estándar',
            'usage_count': 850
        },
        'recent': [
            {'name': 'Plantilla Nueva', 'created_at': '20/10/2024'},
            # ...
        ]
    },
    'quick_stats': {
        'events_count': 45,
        'participants_count': 1250,
        'avg_certificates_per_event': 27.8
    }
}
```

## Mejores Prácticas

1. **Monitoreo Regular**
   - Revisa el dashboard diariamente para detectar anomalías
   - Presta atención a las tendencias en los gráficos

2. **Actualización de Caché**
   - Actualiza manualmente después de importaciones masivas
   - No es necesario actualizar constantemente (el caché se renueva automáticamente)

3. **Interpretación de Datos**
   - Compara las tendencias mes a mes
   - Identifica patrones en las consultas diarias
   - Usa el promedio de certificados por evento para planificar recursos

4. **Rendimiento**
   - En producción, usa Redis para el caché
   - Monitorea los logs para identificar queries lentas
   - Considera aumentar el TTL si el sistema tiene mucha carga

## Seguridad

- ✅ Solo accesible para usuarios staff
- ✅ Protegido por autenticación de Django
- ✅ No expone datos sensibles en URLs
- ✅ Usa el ORM de Django (protección contra SQL injection)
- ✅ Templates escapan datos automáticamente (protección XSS)

## Mantenimiento

### Limpieza de Caché
```bash
# Desde Django shell
python manage.py shell
>>> from certificates.services.dashboard_stats import DashboardStatsService
>>> service = DashboardStatsService()
>>> service.clear_cache()
```

### Verificar Rendimiento
```bash
# Revisar logs
tail -f logs/django.log | grep "Dashboard stats"
```

## Soporte

Para reportar problemas o sugerencias sobre el dashboard:
1. Revisa esta documentación primero
2. Verifica los logs del sistema
3. Contacta al equipo de desarrollo con detalles específicos del problema
