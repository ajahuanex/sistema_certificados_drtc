#!/bin/bash

echo "=========================================="
echo "🔧 APLICANDO CORRECCIÓN REDIS EN SERVIDOR"
echo "=========================================="

# 1. Hacer backup de archivos actuales
echo "📋 1. Haciendo backup de configuración actual..."
cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)
cp config/settings/production.py config/settings/production.py.backup.$(date +%Y%m%d_%H%M%S)
cp docker-compose.prod.yml docker-compose.prod.yml.backup.$(date +%Y%m%d_%H%M%S)

# 2. Agregar USE_REDIS=False al .env.production
echo "📋 2. Configurando USE_REDIS=False..."
if ! grep -q "USE_REDIS" .env.production; then
    echo "" >> .env.production
    echo "# Configuración Redis (False = usar cache en memoria)" >> .env.production
    echo "USE_REDIS=False" >> .env.production
    echo "✅ USE_REDIS=False agregado a .env.production"
else
    sed -i 's/USE_REDIS=.*/USE_REDIS=False/' .env.production
    echo "✅ USE_REDIS actualizado a False"
fi

# 3. Modificar production.py para configuración condicional
echo "📋 3. Actualizando config/settings/production.py..."
cat > temp_cache_config.py << 'EOF'

# Cache Configuration - Conditional Redis/Memory based on USE_REDIS
USE_REDIS = env.bool('USE_REDIS', default=True)

if USE_REDIS:
    try:
        # Verificar si django_redis está disponible
        import django_redis
        
        # Redis Cache Configuration
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
                    'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                },
                'KEY_PREFIX': env('CACHE_KEY_PREFIX', default='certificados_prod'),
                'TIMEOUT': env.int('CACHE_TIMEOUT', default=3600),
            }
        }
        
        # Session Configuration with Redis
        SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
        SESSION_CACHE_ALIAS = 'default'
        
    except ImportError:
        # Fallback a memoria si django_redis no está disponible
        print("WARNING: django_redis no disponible, usando cache en memoria")
        USE_REDIS = False

if not USE_REDIS:
    # Memory Cache Configuration (fallback when Redis is not available)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'certificados-cache',
            'TIMEOUT': env.int('CACHE_TIMEOUT', default=3600),
            'OPTIONS': {
                'MAX_ENTRIES': 1000,
                'CULL_FREQUENCY': 3,
            }
        }
    }
    
    # Session Configuration with Database (fallback when Redis is not available)
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

EOF

# Buscar y reemplazar la configuración de cache en production.py
python3 << 'PYTHON_SCRIPT'
import re

# Leer el archivo
with open('config/settings/production.py', 'r') as f:
    content = f.read()

# Leer la nueva configuración
with open('temp_cache_config.py', 'r') as f:
    new_cache_config = f.read()

# Patrón para encontrar la configuración de cache actual
cache_pattern = r'# Cache Configuration.*?SESSION_CACHE_ALIAS = \'default\''
session_pattern = r'SESSION_COOKIE_AGE = 86400.*?SESSION_COOKIE_SAMESITE = \'Lax\''

# Reemplazar la configuración de cache
content = re.sub(cache_pattern, new_cache_config.strip(), content, flags=re.DOTALL)

# Escribir el archivo actualizado
with open('config/settings/production.py', 'w') as f:
    f.write(content)

print("✅ production.py actualizado con configuración condicional")
PYTHON_SCRIPT

# Limpiar archivo temporal
rm temp_cache_config.py

# 4. Comentar Redis en docker-compose.prod.yml
echo "📋 4. Comentando Redis en docker-compose.prod.yml..."
sed -i '/depends_on:/,/condition: service_healthy/ {
    /redis:/,/condition: service_healthy/ s/^/#/
}' docker-compose.prod.yml

sed -i '/# Redis para cache y sesiones/,/retries: 3/ s/^/#/' docker-compose.prod.yml

echo "✅ Redis comentado en docker-compose.prod.yml"

# 5. Verificar cambios
echo "📋 5. Verificando cambios aplicados..."
echo "USE_REDIS en .env.production:"
grep "USE_REDIS" .env.production

echo ""
echo "Configuración condicional en production.py:"
grep -A 5 "USE_REDIS.*env.bool" config/settings/production.py

echo ""
echo "=========================================="
echo "✅ CORRECCIÓN REDIS APLICADA"
echo "=========================================="
echo "Ahora ejecuta el despliegue:"
echo "docker-compose -f docker-compose.prod.yml down"
echo "docker-compose -f docker-compose.prod.yml build --no-cache web"
echo "docker-compose -f docker-compose.prod.yml up -d db nginx web"
echo "=========================================="