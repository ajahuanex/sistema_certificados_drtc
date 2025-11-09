#!/bin/bash
# Script para probar la configuración de Docker Compose
# Verifica que todos los servicios estén funcionando correctamente

set -e

echo "=========================================="
echo "Test de Docker Compose - Desarrollo"
echo "=========================================="

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Test 1: Verificar que docker-compose.yml existe
echo ""
print_info "Test 1: Verificando archivos de configuración..."
if [ -f "docker-compose.yml" ]; then
    print_success "docker-compose.yml existe"
else
    print_error "docker-compose.yml no encontrado"
    exit 1
fi

if [ -f "docker-compose.prod.yml" ]; then
    print_success "docker-compose.prod.yml existe"
else
    print_error "docker-compose.prod.yml no encontrado"
    exit 1
fi

# Test 2: Validar sintaxis de Docker Compose
echo ""
print_info "Test 2: Validando sintaxis de Docker Compose..."
if docker-compose -f docker-compose.yml config > /dev/null 2>&1; then
    print_success "docker-compose.yml tiene sintaxis válida"
else
    print_error "docker-compose.yml tiene errores de sintaxis"
    exit 1
fi

if docker-compose -f docker-compose.prod.yml config > /dev/null 2>&1; then
    print_success "docker-compose.prod.yml tiene sintaxis válida"
else
    print_error "docker-compose.prod.yml tiene errores de sintaxis"
    exit 1
fi

# Test 3: Verificar servicios definidos
echo ""
print_info "Test 3: Verificando servicios definidos..."

# Desarrollo
DEV_SERVICES=$(docker-compose -f docker-compose.yml config --services)
for service in web db redis; do
    if echo "$DEV_SERVICES" | grep -q "^${service}$"; then
        print_success "Servicio '$service' definido en desarrollo"
    else
        print_error "Servicio '$service' no encontrado en desarrollo"
        exit 1
    fi
done

# Producción
PROD_SERVICES=$(docker-compose -f docker-compose.prod.yml config --services)
for service in web db redis nginx; do
    if echo "$PROD_SERVICES" | grep -q "^${service}$"; then
        print_success "Servicio '$service' definido en producción"
    else
        print_error "Servicio '$service' no encontrado en producción"
        exit 1
    fi
done

# Test 4: Verificar volúmenes persistentes
echo ""
print_info "Test 4: Verificando volúmenes persistentes..."

# Desarrollo
DEV_VOLUMES=$(docker-compose -f docker-compose.yml config --volumes)
for volume in postgres_data_dev redis_data_dev media_files static_files; do
    if echo "$DEV_VOLUMES" | grep -q "^${volume}$"; then
        print_success "Volumen '$volume' definido en desarrollo"
    else
        print_error "Volumen '$volume' no encontrado en desarrollo"
        exit 1
    fi
done

# Producción
PROD_VOLUMES=$(docker-compose -f docker-compose.prod.yml config --volumes)
for volume in postgres_data_prod redis_data_prod; do
    if echo "$PROD_VOLUMES" | grep -q "^${volume}$"; then
        print_success "Volumen '$volume' definido en producción"
    else
        print_error "Volumen '$volume' no encontrado en producción"
        exit 1
    fi
done

# Test 5: Verificar health checks
echo ""
print_info "Test 5: Verificando health checks..."

# Verificar que los servicios tienen health checks definidos
if docker-compose -f docker-compose.yml config | grep -q "healthcheck:"; then
    print_success "Health checks definidos en desarrollo"
else
    print_error "No se encontraron health checks en desarrollo"
    exit 1
fi

if docker-compose -f docker-compose.prod.yml config | grep -q "healthcheck:"; then
    print_success "Health checks definidos en producción"
else
    print_error "No se encontraron health checks en producción"
    exit 1
fi

# Test 6: Verificar redes
echo ""
print_info "Test 6: Verificando configuración de redes..."

if docker-compose -f docker-compose.yml config | grep -q "certificados_network"; then
    print_success "Red personalizada configurada en desarrollo"
else
    print_error "Red personalizada no encontrada en desarrollo"
    exit 1
fi

if docker-compose -f docker-compose.prod.yml config | grep -q "certificados_network"; then
    print_success "Red personalizada configurada en producción"
else
    print_error "Red personalizada no encontrada en producción"
    exit 1
fi

# Test 7: Verificar dependencias entre servicios
echo ""
print_info "Test 7: Verificando dependencias entre servicios..."

if docker-compose -f docker-compose.yml config | grep -q "depends_on:"; then
    print_success "Dependencias configuradas en desarrollo"
else
    print_error "No se encontraron dependencias en desarrollo"
    exit 1
fi

if docker-compose -f docker-compose.prod.yml config | grep -q "depends_on:"; then
    print_success "Dependencias configuradas en producción"
else
    print_error "No se encontraron dependencias en producción"
    exit 1
fi

echo ""
echo "=========================================="
print_success "Todos los tests pasaron exitosamente!"
echo "=========================================="
echo ""
print_info "Para iniciar el entorno de desarrollo:"
echo "  docker-compose up -d"
echo ""
print_info "Para iniciar el entorno de producción:"
echo "  docker-compose -f docker-compose.prod.yml up -d"
echo ""
