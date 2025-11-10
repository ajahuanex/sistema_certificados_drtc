#!/bin/bash

# Script para ejecutar tests de integración de Docker
# Este script verifica el funcionamiento completo de la aplicación en contenedores

set -e  # Salir si hay algún error

echo "=========================================="
echo "Tests de Integración Docker"
echo "=========================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Limpiar contenedores anteriores
print_info "Limpiando contenedores de test anteriores..."
docker-compose -f docker-compose.test.yml down -v 2>/dev/null || true

echo ""
print_info "Construyendo imágenes de test..."
docker-compose -f docker-compose.test.yml build

echo ""
print_info "Iniciando servicios de test..."
docker-compose -f docker-compose.test.yml up -d test-db test-redis

echo ""
print_info "Esperando a que los servicios estén listos..."
sleep 10

# Verificar que PostgreSQL está listo
print_info "Verificando PostgreSQL..."
docker-compose -f docker-compose.test.yml exec -T test-db pg_isready -U test_user -d test_certificados
if [ $? -eq 0 ]; then
    print_status "PostgreSQL está listo"
else
    print_error "PostgreSQL no está disponible"
    docker-compose -f docker-compose.test.yml down -v
    exit 1
fi

# Verificar que Redis está listo
print_info "Verificando Redis..."
docker-compose -f docker-compose.test.yml exec -T test-redis redis-cli ping
if [ $? -eq 0 ]; then
    print_status "Redis está listo"
else
    print_error "Redis no está disponible"
    docker-compose -f docker-compose.test.yml down -v
    exit 1
fi

echo ""
echo "=========================================="
echo "Ejecutando Tests de Integración"
echo "=========================================="
echo ""

# Ejecutar tests de integración Docker
print_info "Ejecutando tests de integración Docker..."
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py test certificates.tests.test_docker_integration --verbosity=2

TEST_EXIT_CODE=$?

echo ""
echo "=========================================="
echo "Ejecutando Tests de Comunicación"
echo "=========================================="
echo ""

# Test de conexión a base de datos
print_info "Test: Conexión a PostgreSQL..."
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py shell -c "
from django.db import connection
try:
    connection.ensure_connection()
    print('✓ Conexión a PostgreSQL exitosa')
except Exception as e:
    print(f'✗ Error de conexión: {e}')
    exit(1)
"

# Test de conexión a Redis
print_info "Test: Conexión a Redis..."
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py shell -c "
from django.core.cache import cache
try:
    cache.set('test_key', 'test_value', 10)
    value = cache.get('test_key')
    if value == 'test_value':
        print('✓ Conexión a Redis exitosa')
    else:
        print('✗ Redis no devolvió el valor correcto')
        exit(1)
except Exception as e:
    print(f'✗ Error de conexión a Redis: {e}')
    exit(1)
"

# Test de migraciones
print_info "Test: Migraciones de base de datos..."
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py migrate --noinput

echo ""
echo "=========================================="
echo "Ejecutando Tests de Persistencia"
echo "=========================================="
echo ""

# Test de persistencia de datos
print_info "Test: Persistencia de datos..."
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py shell -c "
from django.contrib.auth.models import User
from certificates.models import CertificateTemplate

# Crear datos
user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
template = CertificateTemplate.objects.create(
    name='Test Template',
    html_template='<html><body>Test</body></html>',
    is_default=True
)

print(f'✓ Usuario creado: {user.username}')
print(f'✓ Template creado: {template.name}')
"

# Verificar que los datos persisten
print_info "Verificando persistencia después de reinicio..."
docker-compose -f docker-compose.test.yml restart test-web
sleep 5

docker-compose -f docker-compose.test.yml run --rm test-web python manage.py shell -c "
from django.contrib.auth.models import User
from certificates.models import CertificateTemplate

try:
    user = User.objects.get(username='testuser')
    template = CertificateTemplate.objects.get(name='Test Template')
    print('✓ Datos persisten correctamente después de reinicio')
except Exception as e:
    print(f'✗ Error: Los datos no persistieron: {e}')
    exit(1)
"

echo ""
echo "=========================================="
echo "Ejecutando Tests de Health Check"
echo "=========================================="
echo ""

# Test de health check
print_info "Test: Health check endpoint..."
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py shell -c "
from certificates.views.health_views import database_health_check, cache_health_check

db_health = database_health_check()
cache_health = cache_health_check()

if db_health['healthy']:
    print('✓ Database health check: OK')
else:
    print('✗ Database health check: FAILED')
    exit(1)

if cache_health['healthy']:
    print('✓ Cache health check: OK')
else:
    print('✗ Cache health check: FAILED')
    exit(1)
"

echo ""
echo "=========================================="
echo "Limpieza"
echo "=========================================="
echo ""

print_info "Deteniendo y eliminando contenedores de test..."
docker-compose -f docker-compose.test.yml down -v

echo ""
echo "=========================================="
echo "Resumen de Tests"
echo "=========================================="
echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_status "Todos los tests de integración Docker pasaron exitosamente"
    echo ""
    print_info "Los siguientes componentes fueron verificados:"
    echo "  • Conexión a PostgreSQL"
    echo "  • Conexión a Redis"
    echo "  • Comunicación entre servicios"
    echo "  • Persistencia de datos"
    echo "  • Health checks"
    echo "  • Operaciones CRUD"
    echo "  • Transacciones de base de datos"
    echo "  • Cache y sesiones"
    echo ""
    exit 0
else
    print_error "Algunos tests fallaron"
    echo ""
    print_info "Revisa los logs arriba para más detalles"
    echo ""
    exit 1
fi
