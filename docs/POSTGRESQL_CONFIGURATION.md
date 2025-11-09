# Configuración de PostgreSQL para Producción

Este documento describe la configuración de PostgreSQL implementada para el sistema de certificados DRTC en producción.

## Características Implementadas

### 1. Servicio PostgreSQL en Docker Compose

El servicio PostgreSQL está configurado en `docker-compose.prod.yml` con las siguientes características:

- **Imagen**: PostgreSQL 15 Alpine (optimizada para producción)
- **Persistencia**: Volumen nombrado `postgres_data_prod`
- **Health Checks**: Verificación automática de disponibilidad
- **Configuración optimizada**: Parámetros ajustados para producción

### 2. Configuración de Producción

La configuración de Django en `config/settings/production.py` incluye:

#### Connection Pooling
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # Mantiene conexiones abiertas por 10 minutos
        'CONN_HEALTH_CHECKS': True,  # Verifica salud antes de usar
        'ATOMIC_REQUESTS': True,  # Transacciones automáticas por request
    }
}
```

#### Opciones de PostgreSQL
- **connect_timeout**: 10 segundos
- **statement_timeout**: 30 segundos para queries
- **Encoding**: UTF-8
- **Locale**: es_PE.UTF-8

### 3. Variables de Entorno

Las credenciales y configuración se manejan mediante variables de entorno:

```bash
DB_NAME=certificados_prod
DB_USER=certificados_user
DB_PASSWORD=tu_password_seguro
DB_HOST=db
DB_PORT=5432
DB_CONN_MAX_AGE=600
```

### 4. Optimizaciones de PostgreSQL

El contenedor PostgreSQL incluye optimizaciones para producción:

```yaml
command: >
  postgres
  -c max_connections=100
  -c shared_buffers=256MB
  -c effective_cache_size=1GB
  -c maintenance_work_mem=64MB
  -c checkpoint_completion_target=0.9
  -c wal_buffers=16MB
  -c default_statistics_target=100
```

#### Explicación de Parámetros

- **max_connections**: Máximo 100 conexiones simultáneas
- **shared_buffers**: 256MB de memoria compartida para cache
- **effective_cache_size**: 1GB estimado de cache del sistema
- **maintenance_work_mem**: 64MB para operaciones de mantenimiento
- **checkpoint_completion_target**: Optimiza escritura de checkpoints
- **wal_buffers**: 16MB para Write-Ahead Logging
- **default_statistics_target**: Mejora precisión del query planner

## Uso

### Iniciar el Servicio

```bash
# Iniciar todos los servicios
docker-compose -f docker-compose.prod.yml up -d

# Ver logs de PostgreSQL
docker-compose -f docker-compose.prod.yml logs -f db
```

### Verificar Conexión

```bash
# Usando el comando de Django
docker-compose -f docker-compose.prod.yml exec web python manage.py test_database

# Usando health check
curl http://localhost:8181/health/database/
```

### Acceder a PostgreSQL

```bash
# Conectar a la base de datos
docker-compose -f docker-compose.prod.yml exec db psql -U certificados_user -d certificados_prod

# Ejecutar query desde línea de comandos
docker-compose -f docker-compose.prod.yml exec db psql -U certificados_user -d certificados_prod -c "SELECT version();"
```

### Ejecutar Migraciones

```bash
# Aplicar migraciones
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Ver estado de migraciones
docker-compose -f docker-compose.prod.yml exec web python manage.py showmigrations
```

## Backup y Restauración

### Crear Backup

```bash
# Backup manual
docker-compose -f docker-compose.prod.yml exec db pg_dump -U certificados_user certificados_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup comprimido
docker-compose -f docker-compose.prod.yml exec db pg_dump -U certificados_user certificados_prod | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Restaurar Backup

```bash
# Restaurar desde archivo SQL
docker-compose -f docker-compose.prod.yml exec -T db psql -U certificados_user -d certificados_prod < backup.sql

# Restaurar desde archivo comprimido
gunzip -c backup.sql.gz | docker-compose -f docker-compose.prod.yml exec -T db psql -U certificados_user -d certificados_prod
```

## Monitoreo

### Health Checks

El sistema incluye varios endpoints de monitoreo:

```bash
# Health check general
curl http://localhost:8181/health/

# Health check específico de base de datos
curl http://localhost:8181/health/database/

# Health check de cache
curl http://localhost:8181/health/cache/
```

### Estadísticas de Conexiones

```sql
-- Ver conexiones activas
SELECT count(*) FROM pg_stat_activity WHERE datname = 'certificados_prod';

-- Ver detalles de conexiones
SELECT pid, usename, application_name, client_addr, state, query 
FROM pg_stat_activity 
WHERE datname = 'certificados_prod';

-- Ver tamaño de la base de datos
SELECT pg_size_pretty(pg_database_size('certificados_prod'));
```

### Logs

```bash
# Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f db

# Ver últimas 100 líneas
docker-compose -f docker-compose.prod.yml logs --tail=100 db
```

## Troubleshooting

### Problema: No se puede conectar a la base de datos

**Solución**:
```bash
# Verificar que el contenedor está corriendo
docker-compose -f docker-compose.prod.yml ps db

# Verificar health check
docker-compose -f docker-compose.prod.yml exec db pg_isready -U certificados_user

# Revisar logs
docker-compose -f docker-compose.prod.yml logs db
```

### Problema: Conexiones agotadas

**Solución**:
```sql
-- Ver conexiones activas
SELECT count(*) FROM pg_stat_activity;

-- Terminar conexiones inactivas
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'certificados_prod' 
AND state = 'idle' 
AND state_change < current_timestamp - INTERVAL '5 minutes';
```

### Problema: Performance lenta

**Solución**:
```sql
-- Ver queries lentas
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE state = 'active' 
ORDER BY duration DESC;

-- Analizar uso de índices
SELECT schemaname, tablename, indexname, idx_scan 
FROM pg_stat_user_indexes 
ORDER BY idx_scan;
```

## Seguridad

### Mejores Prácticas

1. **Cambiar contraseñas por defecto**: Usar contraseñas fuertes en producción
2. **Limitar conexiones**: Configurar `max_connections` según necesidad
3. **Usar SSL**: Habilitar SSL para conexiones en producción real
4. **Backups regulares**: Configurar backups automáticos diarios
5. **Monitoreo**: Implementar alertas para conexiones y performance

### Configuración SSL (Producción Real)

Para habilitar SSL en producción:

```yaml
# En docker-compose.prod.yml
db:
  command: >
    postgres
    -c ssl=on
    -c ssl_cert_file=/etc/ssl/certs/server.crt
    -c ssl_key_file=/etc/ssl/private/server.key
  volumes:
    - ./ssl/server.crt:/etc/ssl/certs/server.crt:ro
    - ./ssl/server.key:/etc/ssl/private/server.key:ro
```

## Referencias

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Django Database Configuration](https://docs.djangoproject.com/en/stable/ref/databases/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
