#!/bin/bash

echo "=== CORRECCIÓN COMPLETA DEL ARCHIVO .env.production ==="
echo ""

# Crear backup del archivo actual
if [ -f ".env.production" ]; then
    cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)
    echo "✓ Backup creado del archivo actual"
fi

echo "Creando archivo .env.production completo..."

# Crear el archivo .env.production completo
cat > .env.production << 'EOF'
# Variables de Entorno para Producción - Sistema Certificados DRTC
# Configuración para servidor remoto

# =============================================================================
# CONFIGURACIÓN DJANGO
# =============================================================================

DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
SECRET_KEY=clave-temporal-para-desarrollo-y-pruebas-locales-123456789-cambiar-en-produccion-real

# Hosts permitidos
ALLOWED_HOSTS=localhost,127.0.0.1,161.132.47.92,certificados.transportespuno.gob.pe,www.certificados.transportespuno.gob.pe

# CSRF Trusted Origins (para evitar error 403)
CSRF_TRUSTED_ORIGINS=http://localhost:7070,http://127.0.0.1:7070,http://161.132.47.92:7070,http://certificados.transportespuno.gob.pe,http://www.certificados.transportespuno.gob.pe,https://certificados.transportespuno.gob.pe,https://www.certificados.transportespuno.gob.pe

# URLs base
SITE_URL=http://161.132.47.92:7070
ADMIN_URL=admin/

# =============================================================================
# BASE DE DATOS POSTGRESQL
# =============================================================================

DB_ENGINE=django.db.backends.postgresql
DB_NAME=certificados_prod
DB_USER=certificados_user
DB_PASSWORD=certificados_password_123
DB_HOST=postgres
DB_PORT=5432

# Variables para PostgreSQL Container
POSTGRES_DB=certificados_prod
POSTGRES_USER=certificados_user
POSTGRES_PASSWORD=certificados_password_123

# Configuración de conexiones persistentes (en segundos)
DB_CONN_MAX_AGE=600

# =============================================================================
# REDIS (CACHE Y SESIONES)
# =============================================================================

REDIS_URL=redis://:redis_password@redis:6379/0
REDIS_PASSWORD=redis_password

# Configuración de cache
CACHE_TIMEOUT=3600
CACHE_KEY_PREFIX=certificados_prod

# =============================================================================
# CONFIGURACIÓN DE EMAIL (DESHABILITADO PARA PRUEBAS)
# =============================================================================

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=Sistema de Certificados DRTC <certificados@transportespuno.gob.pe>

# =============================================================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# =============================================================================

STATIC_URL=/static/
STATIC_ROOT=/app/staticfiles
MEDIA_URL=/media/
MEDIA_ROOT=/app/media

# =============================================================================
# CONFIGURACIÓN ESPECÍFICA DRTC
# =============================================================================

INSTITUTION_NAME=Dirección Regional de Transportes y Comunicaciones - Puno
INSTITUTION_SHORT_NAME=DRTC Puno
INSTITUTION_ADDRESS=Jr. Deustua 356, Puno, Perú
INSTITUTION_PHONE=+51 51 351234
INSTITUTION_EMAIL=info@transportespuno.gob.pe

# =============================================================================
# CONFIGURACIÓN DE PERFORMANCE
# =============================================================================

GUNICORN_WORKERS=2
GUNICORN_TIMEOUT=300

# =============================================================================
# HEALTH CHECKS
# =============================================================================

HEALTH_CHECK_ENABLED=True

# =============================================================================
# CONFIGURACIÓN DE SEGURIDAD SSL/HTTPS
# =============================================================================
# Para pruebas locales sin HTTPS, mantener en False
# En producción real con certificado SSL, cambiar a True

SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
EOF

echo "✓ Archivo .env.production creado"
echo ""

# Actualizar docker-compose.prod.yml para Redis con contraseña
echo "Actualizando docker-compose.prod.yml para Redis con contraseña..."

# Crear backup
cp docker-compose.prod.yml docker-compose.prod.yml.backup.$(date +%Y%m%d_%H%M%S)

# Actualizar la configuración de Redis
python3 << 'EOFPYTHON'
import re

# Leer archivo
with open('docker-compose.prod.yml', 'r') as f:
    content = f.read()

# Buscar y reemplazar la sección de Redis
redis_pattern = r'(  redis:.*?)(healthcheck:.*?retries: 3)'
redis_replacement = r'''  redis:
    image: redis:7-alpine
    container_name: certificados_redis_prod
    restart: unless-stopped
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD:-redis_password}
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
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD:-redis_password}", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3'''

content = re.sub(redis_pattern, redis_replacement, content, flags=re.DOTALL)

# Escribir archivo
with open('docker-compose.prod.yml', 'w') as f:
    f.write(content)

print("✓ docker-compose.prod.yml actualizado")
EOFPYTHON

echo ""
echo "Reiniciando servicios con nueva configuración..."

# Detener servicios
docker compose -f docker-compose.prod.yml down

# Limpiar volumen de Redis para evitar problemas de autenticación
docker volume rm sistema_certificados_drtc_redis_data_prod 2>/dev/null || echo "Volumen Redis no existía"

# Iniciar servicios
docker compose -f docker-compose.prod.yml up -d

echo ""
echo "Esperando que los servicios estén listos..."
sleep 45

echo ""
echo "=== VERIFICACIÓN FINAL ==="

echo "Estado de servicios:"
docker compose -f docker-compose.prod.yml ps

echo ""
echo "Prueba Redis con contraseña:"
docker compose -f docker-compose.prod.yml exec redis redis-cli -a redis_password ping

echo ""
echo "Prueba PostgreSQL:"
docker compose -f docker-compose.prod.yml exec postgres pg_isready -U certificados_user -d certificados_prod

echo ""
echo "Prueba aplicación web:"
curl -I http://localhost:7070/admin/ 2>/dev/null | head -1 || echo "Aplicación aún no responde"

echo ""
echo "Logs recientes del servicio web:"
docker compose -f docker-compose.prod.yml logs web --tail=5

echo ""
echo "=== CORRECCIÓN COMPLETADA ==="
echo "La aplicación debería estar disponible en: http://161.132.47.92:7070"
echo ""
echo "Para monitorear:"
echo "docker compose -f docker-compose.prod.yml logs web -f"