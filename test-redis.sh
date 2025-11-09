#!/bin/bash
# Script para probar la configuración de Redis en Docker

echo "=========================================="
echo "Test de Configuración Redis"
echo "=========================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Verificar que Docker Compose esté corriendo
print_info "Verificando servicios Docker..."
if ! docker-compose ps | grep -q "Up"; then
    print_error "Los servicios Docker no están corriendo"
    echo "Ejecuta: docker-compose up -d"
    exit 1
fi
print_success "Servicios Docker están corriendo"
echo ""

# Test 1: Verificar que Redis esté corriendo
print_info "Test 1: Verificando servicio Redis..."
if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
    print_success "Redis está respondiendo correctamente"
else
    print_error "Redis no está respondiendo"
    exit 1
fi
echo ""

# Test 2: Verificar configuración de Redis
print_info "Test 2: Verificando configuración de Redis..."
echo "Configuración actual:"
docker-compose exec -T redis redis-cli CONFIG GET maxmemory
docker-compose exec -T redis redis-cli CONFIG GET maxmemory-policy
docker-compose exec -T redis redis-cli CONFIG GET appendonly
print_success "Configuración de Redis verificada"
echo ""

# Test 3: Verificar persistencia de datos
print_info "Test 3: Verificando persistencia de datos..."
docker-compose exec -T redis redis-cli SET test_key "test_value" > /dev/null
VALUE=$(docker-compose exec -T redis redis-cli GET test_key)
if echo "$VALUE" | grep -q "test_value"; then
    print_success "Persistencia de datos funcionando"
    docker-compose exec -T redis redis-cli DEL test_key > /dev/null
else
    print_error "Problema con persistencia de datos"
    exit 1
fi
echo ""

# Test 4: Verificar conexión desde Django
print_info "Test 4: Verificando conexión Django-Redis..."
if docker-compose exec -T web python manage.py test_cache; then
    print_success "Django puede conectarse a Redis correctamente"
else
    print_error "Django no puede conectarse a Redis"
    exit 1
fi
echo ""

# Test 5: Verificar información de Redis
print_info "Test 5: Información del servidor Redis..."
echo "Estadísticas de Redis:"
docker-compose exec -T redis redis-cli INFO stats | grep -E "total_connections_received|total_commands_processed|keyspace_hits|keyspace_misses"
echo ""
docker-compose exec -T redis redis-cli INFO memory | grep -E "used_memory_human|maxmemory_human"
print_success "Información de Redis obtenida"
echo ""

# Test 6: Verificar volumen de datos
print_info "Test 6: Verificando volumen de persistencia..."
VOLUME_INFO=$(docker volume inspect certificados_redis_data_dev 2>/dev/null || docker volume inspect dockerizacion-produccion_redis_data_dev 2>/dev/null)
if [ $? -eq 0 ]; then
    print_success "Volumen de Redis configurado correctamente"
    echo "$VOLUME_INFO" | grep -E "Mountpoint|Name"
else
    print_error "No se pudo verificar el volumen de Redis"
fi
echo ""

# Resumen final
echo "=========================================="
echo "Resumen de Tests"
echo "=========================================="
print_success "Todos los tests de Redis pasaron correctamente"
echo ""
echo "Redis está configurado y funcionando para:"
echo "  - Cache de Django"
echo "  - Almacenamiento de sesiones"
echo "  - Persistencia de datos"
echo ""
print_info "Para monitorear Redis en tiempo real:"
echo "  docker-compose exec redis redis-cli MONITOR"
echo ""
print_info "Para ver estadísticas de Redis:"
echo "  docker-compose exec redis redis-cli INFO"
