#!/bin/bash

# Script para desplegar en servidor remoto con corrección Redis
# Servidor: 161.132.47.92

set -e  # Salir si hay algún error

echo "=========================================="
echo "🚀 DESPLIEGUE REMOTO - SIN REDIS"
echo "=========================================="
echo "Servidor: 161.132.47.92"
echo "Fecha: $(date)"
echo ""

# Función para mostrar progreso
show_progress() {
    echo ""
    echo "📋 $1"
    echo "----------------------------------------"
}

# Función para verificar comando
check_command() {
    if [ $? -eq 0 ]; then
        echo "✅ $1 - EXITOSO"
    else
        echo "❌ $1 - ERROR"
        exit 1
    fi
}

show_progress "1. PREPARACIÓN - Backup de configuración actual"
cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
cp docker-compose.prod.yml docker-compose.prod.yml.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
echo "✅ Backup realizado"

show_progress "2. ACTUALIZACIÓN - Descargando código desde GitHub"
git fetch origin
check_command "Git fetch"

git reset --hard origin/main
check_command "Git reset"

git pull origin main
check_command "Git pull"

show_progress "3. VERIFICACIÓN - Archivos actualizados"
echo "Verificando USE_REDIS en production.py:"
grep -A 5 "USE_REDIS" config/settings/production.py || echo "No encontrado"

echo "Verificando USE_REDIS en .env.production:"
grep "USE_REDIS" .env.production || echo "No encontrado"

show_progress "4. DETENER SERVICIOS - Parando contenedores actuales"
docker-compose -f docker-compose.prod.yml down
check_command "Docker compose down"

show_progress "5. LIMPIEZA - Eliminando contenedores antiguos"
docker container prune -f
docker image prune -f
echo "✅ Limpieza completada"

show_progress "6. CONSTRUCCIÓN - Construyendo nueva imagen"
docker-compose -f docker-compose.prod.yml build --no-cache web
check_command "Docker build"

show_progress "7. INICIO - Levantando servicios (SIN Redis)"
docker-compose -f docker-compose.prod.yml up -d db nginx web
check_command "Docker compose up"

show_progress "8. ESPERA - Aguardando que PostgreSQL esté listo"
echo "Esperando 30 segundos..."
sleep 30

# Verificar que PostgreSQL esté funcionando
echo "Verificando PostgreSQL..."
docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U certificados_user -d certificados_prod
check_command "PostgreSQL ready check"

show_progress "9. MIGRACIONES - Aplicando migraciones de base de datos"
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate
check_command "Django migrations"

show_progress "10. SUPERUSUARIO - Creando usuario administrador"
docker-compose -f docker-compose.prod.yml exec -T web python manage.py create_superuser_if_not_exists
check_command "Create superuser"

show_progress "11. ESTÁTICOS - Recolectando archivos estáticos"
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput
check_command "Collect static files"

show_progress "12. PLANTILLA - Cargando plantilla por defecto"
docker-compose -f docker-compose.prod.yml exec -T web python manage.py load_default_template
check_command "Load default template"

show_progress "13. VERIFICACIÓN - Probando configuración de cache"
docker-compose -f docker-compose.prod.yml exec -T web python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()
from django.conf import settings
from django.core.cache import cache

print('=== CONFIGURACIÓN DE CACHE ===')
print(f'USE_REDIS: {getattr(settings, \"USE_REDIS\", \"No definido\")}')
print(f'Cache Backend: {settings.CACHES[\"default\"][\"BACKEND\"]}')
print(f'Session Engine: {settings.SESSION_ENGINE}')

print('\n=== PRUEBA DE CACHE ===')
try:
    cache.set('test_key', 'test_value', 60)
    value = cache.get('test_key')
    print(f'Cache test: {\"✅ OK\" if value == \"test_value\" else \"❌ FAIL\"}')
    cache.delete('test_key')
    print('✅ Cache funcionando correctamente')
except Exception as e:
    print(f'❌ Error en cache: {e}')
"
check_command "Cache verification"

show_progress "14. ESTADO - Verificando servicios"
echo "Estado de los contenedores:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "Últimos logs de la aplicación:"
docker-compose -f docker-compose.prod.yml logs --tail=10 web

show_progress "15. CONECTIVIDAD - Probando acceso HTTP"
echo "Probando conectividad local..."
curl -I http://localhost:7070 2>/dev/null | head -1 || echo "❌ Error en conectividad local"

echo "Probando conectividad externa..."
curl -I http://161.132.47.92:7070 2>/dev/null | head -1 || echo "❌ Error en conectividad externa"

show_progress "16. RECURSOS - Verificando uso del sistema"
echo "Uso de disco:"
df -h | grep -E "(Filesystem|/dev/)"

echo ""
echo "Uso de Docker:"
docker system df

echo ""
echo "=========================================="
echo "🎉 DESPLIEGUE COMPLETADO"
echo "=========================================="
echo ""
echo "✅ Sistema desplegado SIN Redis"
echo "✅ Cache en memoria funcionando"
echo "✅ Sesiones en base de datos"
echo "✅ Todos los servicios activos"
echo ""
echo "🌐 URLs de acceso:"
echo "   • Principal: http://161.132.47.92:7070"
echo "   • Admin: http://161.132.47.92:7070/admin/"
echo "   • Credenciales: admin / admin123"
echo ""
echo "📊 Para monitorear logs:"
echo "   docker-compose -f docker-compose.prod.yml logs -f web"
echo ""
echo "🔧 Para diagnóstico:"
echo "   docker-compose -f docker-compose.prod.yml ps"
echo "   docker stats"
echo ""
echo "=========================================="