# Dashboard de Estadísticas - Guía de Usuario

## Introducción

El Dashboard de Estadísticas del Sistema de Certificados DRTC Puno proporciona una vista completa y en tiempo real del estado del sistema, con métricas clave, gráficos interactivos y estadísticas detalladas.

## Acceso al Dashboard

### Desde el Panel de Administración

1. Inicia sesión en el panel de administración: `/admin/`
2. En la página principal verás un banner destacado con el enlace al Dashboard
3. Haz clic en **"🚀 Ver Dashboard"**

### Acceso Directo

- URL directa: `/certificates/admin/dashboard/`
- **Requisito**: Debes tener permisos de staff (administrador)

## Características del Dashboard

### 📊 Métricas Principales

El dashboard muestra 6 métricas clave en la parte superior:

#### 1. Total de Eventos
- **Descripción**: Número total de eventos registrados en el sistema
- **Tendencia**: Muestra eventos creados en el último mes
- **Color**: Azul (estándar)

#### 2. Certificados Generados
- **Descripción**: Total de certificados PDF generados
- **Tendencia**: Certificados generados en el último mes
- **Color**: Verde (éxito)

#### 3. Certificados Firmados
- **Descripción**: Certificados que han sido firmados digitalmente
- **Tendencia**: Porcentaje del total de certificados
- **Color**: Azul (información)

#### 4. Pendientes de Firma
- **Descripción**: Certificados generados pero sin firma digital
- **Tendencia**: Porcentaje del total de certificados
- **Color**: Amarillo (advertencia)

#### 5. Total Participantes
- **Descripción**: Número total de participantes registrados
- **Tendencia**: Promedio de participantes por evento
- **Color**: Azul (información)

#### 6. Verificaciones (30 días)
- **Descripción**: Número de verificaciones de certificados en los últimos 30 días
- **Tendencia**: Actividad de verificación
- **Color**: Verde (éxito)

### 📈 Gráficos Interactivos

El dashboard incluye 5 gráficos principales:

#### 1. Certificados por Mes
- **Tipo**: Gráfico de línea
- **Período**: Últimos 12 meses
- **Descripción**: Muestra la tendencia de generación de certificados
- **Uso**: Identificar picos de actividad y patrones estacionales

#### 2. Eventos por Mes
- **Tipo**: Gráfico de línea
- **Período**: Últimos 12 meses
- **Descripción**: Tendencia de creación de eventos
- **Uso**: Planificación de capacidad y recursos

#### 3. Verificaciones Diarias
- **Tipo**: Gráfico de línea
- **Período**: Últimos 30 días
- **Descripción**: Actividad diaria de verificación de certificados
- **Uso**: Monitorear el uso público del sistema

#### 4. Tipos de Participantes
- **Tipo**: Gráfico de dona
- **Descripción**: Distribución porcentual por tipo de participante
- **Categorías**: Asistentes, Ponentes, Organizadores
- **Uso**: Análisis demográfico de participantes

#### 5. Estado de Firmas
- **Tipo**: Gráfico de dona
- **Descripción**: Proporción de certificados firmados vs sin firmar
- **Categorías**: Firmados Digitalmente, Sin Firma
- **Uso**: Monitorear el proceso de firma digital

### 📋 Tablas de Datos

#### 1. Eventos Recientes
- **Contenido**: Los 5 eventos más recientes
- **Columnas**: Nombre del evento, Fecha, Número de participantes
- **Ordenamiento**: Por fecha de creación (más reciente primero)

#### 2. Certificados Recientes
- **Contenido**: Los 5 certificados generados más recientemente
- **Columnas**: Participante, Evento, Estado de firma
- **Estados**: 
  - 🟢 **Firmado**: Certificado con firma digital
  - 🟡 **Sin Firma**: Certificado pendiente de firma

#### 3. Estadísticas por Tipo
- **Contenido**: Distribución de participantes por tipo
- **Columnas**: Tipo de participante, Cantidad, Porcentaje
- **Tipos**:
  - 👤 **Asistentes**: Participantes regulares
  - 🎤 **Ponentes**: Expositores y presentadores
  - 👔 **Organizadores**: Personal organizador

#### 4. Actividad Reciente
- **Contenido**: Los 10 registros de auditoría más recientes
- **Columnas**: Tipo de acción, Usuario, Fecha
- **Acciones**:
  - 📥 **Importación**: Carga de participantes desde Excel
  - 📜 **Generación**: Creación de certificados PDF
  - ✍️ **Firma**: Firma digital de certificados
  - 🔍 **Consulta**: Búsqueda pública por DNI
  - ✅ **Verificación**: Verificación por código QR

## Funcionalidades Avanzadas

### 🔄 Actualización Automática

- **Auto-refresh**: El dashboard se actualiza automáticamente cada 5 minutos
- **Actualización manual**: Botón "🔄 Actualizar" en la esquina superior derecha
- **Timestamp**: Muestra la hora de la última actualización

### 📱 Diseño Responsive

- **Adaptable**: Se ajusta automáticamente a diferentes tamaños de pantalla
- **Mobile-friendly**: Funciona correctamente en tablets y móviles
- **Grid flexible**: Los elementos se reorganizan según el espacio disponible

### ⚡ Performance Optimizada

- **Queries eficientes**: Uso de `select_related` para minimizar consultas a la base de datos
- **Carga asíncrona**: Los gráficos se cargan de forma asíncrona
- **Cache inteligente**: Datos optimizados para reducir tiempo de carga

## API del Dashboard

El dashboard expone APIs REST para obtener datos específicos:

### Endpoint de Gráficos
```
GET /certificates/admin/dashboard/charts/?chart=<tipo>
```

**Tipos disponibles:**
- `certificates_by_month`: Datos del gráfico de certificados por mes
- `events_by_month`: Datos del gráfico de eventos por mes
- `verifications_by_day`: Datos del gráfico de verificaciones diarias
- `attendee_types`: Datos del gráfico de tipos de participantes
- `signature_status`: Datos del gráfico de estado de firmas

### Endpoint de Estadísticas
```
GET /certificates/admin/dashboard/stats/?stat=<tipo>
```

**Tipos disponibles:**
- `overview`: Estadísticas generales del sistema
- `performance`: Métricas de rendimiento
- `activity`: Estadísticas de actividad por hora

## Casos de Uso

### 1. Monitoreo Diario
- Revisar métricas principales al inicio del día
- Verificar certificados pendientes de firma
- Monitorear actividad de verificaciones

### 2. Análisis Mensual
- Revisar tendencias de certificados generados
- Analizar distribución de tipos de participantes
- Evaluar efectividad de eventos

### 3. Planificación de Recursos
- Identificar picos de actividad
- Planificar capacidad de firma digital
- Optimizar procesos basado en datos

### 4. Reportes Ejecutivos
- Generar insights para reportes gerenciales
- Identificar KPIs del sistema
- Monitorear adopción y uso

## Solución de Problemas

### Dashboard No Carga
1. **Verificar permisos**: Asegúrate de tener permisos de staff
2. **Revisar logs**: Consultar `logs/certificates.log` para errores
3. **Verificar base de datos**: Confirmar conectividad a la base de datos

### Gráficos No Se Muestran
1. **JavaScript habilitado**: Verificar que JavaScript esté habilitado en el navegador
2. **CDN de Chart.js**: Confirmar acceso a `cdn.jsdelivr.net`
3. **Consola del navegador**: Revisar errores en la consola de desarrollador

### Datos Incorrectos
1. **Cache del navegador**: Hacer hard refresh (Ctrl+F5)
2. **Actualización manual**: Usar el botón "Actualizar"
3. **Verificar datos fuente**: Confirmar datos en el admin de Django

### Performance Lenta
1. **Volumen de datos**: El dashboard puede ser lento con >10,000 registros
2. **Optimización de base de datos**: Ejecutar `VACUUM` en PostgreSQL
3. **Índices**: Verificar que los índices estén creados correctamente

## Datos de Prueba

Para probar el dashboard con datos de muestra:

```bash
# Generar datos de prueba
python manage.py generate_sample_data

# Generar más datos específicos
python manage.py generate_sample_data --events 20 --participants-per-event 25

# Limpiar y regenerar
python manage.py generate_sample_data --clear --events 15
```

## Personalización

### Modificar Métricas
Para agregar nuevas métricas, editar:
- `certificates/views/dashboard_views.py` - Lógica de backend
- `templates/admin/certificates/dashboard.html` - Frontend

### Agregar Gráficos
1. Crear método en `DashboardChartsAPIView`
2. Agregar canvas en el template HTML
3. Implementar JavaScript para el gráfico

### Cambiar Colores
Modificar los colores en el CSS del template:
```css
.stat-card.success { border-left-color: #28a745; }
.stat-card.warning { border-left-color: #ffc107; }
.stat-card.danger { border-left-color: #dc3545; }
.stat-card.info { border-left-color: #17a2b8; }
```

## Mejores Prácticas

### Para Administradores
1. **Revisar diariamente**: Hacer un check rápido de las métricas principales
2. **Monitorear tendencias**: Prestar atención a cambios significativos
3. **Actuar sobre alertas**: Investigar anomalías en los datos

### Para Desarrolladores
1. **Optimizar queries**: Usar `select_related` y `prefetch_related`
2. **Cache inteligente**: Implementar cache para datos que no cambian frecuentemente
3. **Monitorear performance**: Usar Django Debug Toolbar en desarrollo

### Para el Sistema
1. **Backup regular**: Los datos del dashboard dependen de la integridad de la base de datos
2. **Monitoreo de logs**: Revisar logs regularmente para detectar problemas
3. **Actualizaciones**: Mantener Chart.js y otras dependencias actualizadas

## Roadmap Futuro

### Características Planificadas
- **Filtros de fecha**: Permitir filtrar datos por rangos de fecha personalizados
- **Exportación**: Exportar gráficos y datos a PDF/Excel
- **Alertas**: Notificaciones automáticas para métricas críticas
- **Dashboard personalizable**: Permitir a usuarios personalizar widgets
- **Comparación temporal**: Comparar períodos (mes actual vs anterior)

### Integraciones Futuras
- **Google Analytics**: Integración con analytics web
- **Slack/Teams**: Notificaciones a canales de trabajo
- **API externa**: Exposición de métricas para sistemas externos
- **Mobile app**: Aplicación móvil para consulta rápida

---

**Versión**: 1.0  
**Fecha**: Octubre 2024  
**Autor**: Sistema de Certificados DRTC Puno