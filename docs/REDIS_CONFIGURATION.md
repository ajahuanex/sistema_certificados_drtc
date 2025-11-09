# Configuración de Redis para Cache y Sesiones

## Descripción General

Redis está configurado como sistema de cache y almacenamiento de sesiones para mejorar el rendimiento de la aplicación Django. Esta configuración proporciona:

- **Cache de alto rendimiento**: Almacenamiento en memoria para datos frecuentemente accedidos
- **Sesiones de usuario**: Almacenamiento rápido y escalable de sesiones
- **Persistencia de datos**: Configuración AOF (Append Only File) para durabilidad

## Arquitectura

```
┌─────────────────┐
│  Django App     │
│                 │
│  - Views        │
│  - Models       │
│  - Sessions     │
└────────┬────────┘
         │
         │ django-redis
         │
         ▼
┌─────────────────┐
│  Redis Server   │
│                 │
│  - Cache        │
│  - Sessions     │
│  - Persistence  │
└─────────────────┘
```

## Configuración de Docker Compose

### Desarrollo (docker-compose.yml)

```yaml
redis:
  image: redis:7-alpine
  container_name: certificados_redis_dev
  restart: unless-stopped
  command: redis-server --appendonly yes --maxmemory 128mb --maxmemory-policy allkeys-lru
  ports:
    - "6379:6379"
  volumes:
    - redis_data_dev:/data
  networks:
    - certificados_network
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### Producción (docker-compose.prod.yml)

```yaml
redis:
  image: redis:7-alpine
  container_name: certificados_redis_prod
  restart: unless-stopped
  command: >
    redis-server
    --appendonly yes
    --maxmemory 512mb
    --maxmemory-policy allkeys-lru
    --save 900 1
    --save 300 10
    --save 60 10000
  volumes:
    - redis_data_prod:/data
  networks:
    - certificados_network
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 30s
    timeout: 10s
    retries: 3
```

## Configuración de Django

### Base Settings (config/settings/base.py)

```python
# Cache Configuration with Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://redis:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': env('CACHE_KEY_PREFIX', default='certificados'),
        'TIMEOUT': env.int('CACHE_TIMEOUT', default=300),  # 5 minutos
    }
}

# Session Configuration with Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

### Production Settings (config/settings/production.py)

```python
# Cache Configuration - Override para producción
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://redis:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'KEY_PREFIX': env('CACHE_KEY_PREFIX', default='certificados_prod'),
        'TIMEOUT': env.int('CACHE_TIMEOUT', default=3600),  # 1 hora
    }
}
```

## Variables de Entorno

### .env (Desarrollo)

```bash
REDIS_URL=redis://redis:6379/0
CACHE_TIMEOUT=300
CACHE_KEY_PREFIX=certificados
```

### .env.production (Producción)

```bash
REDIS_URL=redis://redis:6379/0
CACHE_TIMEOUT=3600
CACHE_KEY_PREFIX=certificados_prod
```

## Parámetros de Configuración Redis

### Memoria

- **maxmemory**: Límite de memoria para Redis
  - Desarrollo: 128MB
  - Producción: 512MB
  
- **maxmemory-policy**: Política de evicción cuando se alcanza el límite
  - `allkeys-lru`: Elimina las claves menos recientemente usadas

### Persistencia

- **appendonly**: Habilita persistencia AOF (Append Only File)
  - Garantiza durabilidad de datos
  
- **save**: Snapshots automáticos (solo producción)
  - `save 900 1`: Guardar si al menos 1 clave cambió en 900 segundos
  - `save 300 10`: Guardar si al menos 10 claves cambiaron en 300 segundos
  - `save 60 10000`: Guardar si al menos 10000 claves cambiaron en 60 segundos

## Uso en el Código

### Cache Básico

```python
from django.core.cache import cache

# Guardar en cache
cache.set('mi_clave', 'mi_valor', timeout=300)

# Obtener de cache
valor = cache.get('mi_clave')

# Eliminar de cache
cache.delete('mi_clave')

# Cache múltiple
cache.set_many({'clave1': 'valor1', 'clave2': 'valor2'}, timeout=300)
valores = cache.get_many(['clave1', 'clave2'])
```

### Decorador de Cache en Views

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # Cache por 15 minutos
def mi_vista(request):
    # Vista costosa
    return render(request, 'template.html', context)
```

### Cache de Template Fragments

```django
{% load cache %}

{% cache 500 sidebar request.user.username %}
    <!-- Contenido costoso de renderizar -->
{% endcache %}
```

### Cache de Querysets

```python
from django.core.cache import cache

def get_certificados_activos():
    cache_key = 'certificados_activos'
    certificados = cache.get(cache_key)
    
    if certificados is None:
        certificados = list(Certificate.objects.filter(is_active=True))
        cache.set(cache_key, certificados, timeout=300)
    
    return certificados
```

## Testing

### Comando de Test

```bash
# Desarrollo
docker-compose exec web python manage.py test_cache

# Producción
docker-compose -f docker-compose.prod.yml exec web python manage.py test_cache
```

### Script de Test Completo

```bash
# Linux/Mac
./test-redis.sh

# Windows
test-redis.bat
```

### Tests Incluidos

1. ✓ Verificación de servicio Redis
2. ✓ Configuración de Redis
3. ✓ Persistencia de datos
4. ✓ Conexión Django-Redis
5. ✓ Estadísticas de Redis
6. ✓ Volumen de persistencia

## Monitoreo

### Comandos Útiles

```bash
# Ver estadísticas en tiempo real
docker-compose exec redis redis-cli MONITOR

# Información del servidor
docker-compose exec redis redis-cli INFO

# Estadísticas de memoria
docker-compose exec redis redis-cli INFO memory

# Estadísticas de comandos
docker-compose exec redis redis-cli INFO stats

# Ver todas las claves
docker-compose exec redis redis-cli KEYS "*"

# Ver valor de una clave
docker-compose exec redis redis-cli GET "clave"

# Limpiar toda la cache
docker-compose exec redis redis-cli FLUSHALL
```

### Métricas Importantes

- **used_memory**: Memoria utilizada por Redis
- **connected_clients**: Clientes conectados
- **total_commands_processed**: Total de comandos procesados
- **keyspace_hits**: Aciertos de cache
- **keyspace_misses**: Fallos de cache
- **evicted_keys**: Claves evictadas por política de memoria

## Troubleshooting

### Redis no responde

```bash
# Verificar estado del contenedor
docker-compose ps redis

# Ver logs de Redis
docker-compose logs redis

# Reiniciar Redis
docker-compose restart redis
```

### Django no puede conectarse a Redis

```bash
# Verificar variable de entorno
docker-compose exec web env | grep REDIS_URL

# Verificar conectividad de red
docker-compose exec web ping redis

# Verificar que Redis esté en la misma red
docker network inspect certificados_network
```

### Problemas de memoria

```bash
# Ver uso de memoria
docker-compose exec redis redis-cli INFO memory

# Limpiar cache manualmente
docker-compose exec redis redis-cli FLUSHALL

# Ajustar maxmemory en docker-compose.yml
```

### Pérdida de datos

```bash
# Verificar persistencia AOF
docker-compose exec redis redis-cli CONFIG GET appendonly

# Verificar volumen de datos
docker volume inspect certificados_redis_data_dev

# Backup manual
docker-compose exec redis redis-cli BGSAVE
```

## Optimización

### Para Alto Tráfico

1. Aumentar `maxmemory` según recursos disponibles
2. Ajustar `max_connections` en Django settings
3. Considerar Redis Cluster para escalabilidad horizontal
4. Implementar cache warming para datos críticos

### Para Mejor Rendimiento

1. Usar `PARSER_CLASS: 'redis.connection.HiredisParser'` (producción)
2. Habilitar compresión con `COMPRESSOR` (producción)
3. Ajustar timeouts según patrones de uso
4. Implementar cache invalidation estratégica

### Para Mejor Persistencia

1. Ajustar frecuencia de snapshots según necesidades
2. Considerar RDB + AOF para máxima durabilidad
3. Implementar backups regulares del volumen
4. Monitorear tamaño del archivo AOF

## Seguridad

### Recomendaciones

1. **No exponer puerto Redis públicamente**: Solo accesible dentro de la red Docker
2. **Usar contraseña en producción**: Configurar `requirepass` en Redis
3. **Limitar comandos peligrosos**: Deshabilitar FLUSHALL, CONFIG en producción
4. **Encriptar datos sensibles**: Antes de almacenar en cache
5. **Implementar rate limiting**: Para prevenir abuso

### Configuración de Contraseña (Producción)

```yaml
# docker-compose.prod.yml
redis:
  command: redis-server --requirepass ${REDIS_PASSWORD}
  
# .env.production
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
REDIS_PASSWORD=tu_password_seguro_aqui
```

## Referencias

- [Django Cache Framework](https://docs.djangoproject.com/en/5.1/topics/cache/)
- [django-redis Documentation](https://github.com/jazzband/django-redis)
- [Redis Documentation](https://redis.io/documentation)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
