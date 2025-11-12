#!/bin/bash
# Script de Despliegue para Ubuntu Server
# Sistema de Certificados DRTC

set -e  # Salir si hay algún error

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
    echo ""
}

# Verificar que estamos en un repositorio Git
if [ ! -d ".git" ]; then
    print_error "No estás en un repositorio Git"
    exit 1
fi

print_header "🚀 Despliegue en Ubuntu Server"
print_info "Sistema de Certificados DRTC"
print_info "Dominio: certificados.transportespuno.gob.pe"
echo ""

# Verificar Docker
print_info "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado"
    print_info "Instala Docker con: curl -fsSL https://get.docker.com | sh"
    exit 1
fi
print_success "Docker instalado: $(docker --version)"

# Verificar Docker Compose
if ! docker compose version &> /dev/null; then
    print_error "Docker Compose v2 no está disponible"
    exit 1
fi
print_success "Docker Compose: $(docker compose version)"

echo ""
read -p "¿Continuar con el despliegue? (s/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    print_warning "Despliegue cancelado"
    exit 0
fi

# PASO 1: Actualizar código desde GitHub
print_header "📥 PASO 1: Actualizar código desde GitHub"

print_info "Guardando cambios locales..."
git stash

print_info "Obteniendo últimos cambios..."
BRANCH=$(git branch --show-current)
print_info "Rama actual: $BRANCH"

if git pull origin $BRANCH; then
    print_success "Código actualizado desde GitHub"
else
    print_error "Error al actualizar código"
    git stash pop
    exit 1
fi

# Restaurar cambios locales si los había
if git stash list | grep -q "stash@{0}"; then
    print_info "Restaurando cambios locales..."
    git stash pop
fi

# PASO 2: Verificar configuración
print_header "⚙️ PASO 2: Verificar configuración"

if [ ! -f ".env.production" ]; then
    print_warning ".env.production no existe"
    if [ -f ".env.production.example" ]; then
        print_info "Creando .env.production desde ejemplo..."
        cp .env.production.example .env.production
        print_warning "IMPORTANTE: Edita .env.production con tus valores reales"
        print_info "Ejecuta: nano .env.production"
        read -p "Presiona Enter cuando hayas configurado .env.production..."
    else
        print_error ".env.production.example no encontrado"
        exit 1
    fi
else
    print_success ".env.production encontrado"
fi

# PASO 3: Detener servicios anteriores
print_header "🛑 PASO 3: Detener servicios anteriores"

print_info "Deteniendo contenedores..."
if docker compose -f docker-compose.prod.yml down; then
    print_success "Contenedores detenidos"
else
    print_warning "No había contenedores corriendo"
fi

# PASO 4: Construir imágenes
print_header "🔨 PASO 4: Construir imágenes"

print_info "Construyendo imagen web (esto puede tomar varios minutos)..."
if docker compose -f docker-compose.prod.yml build --no-cache web; then
    print_success "Imagen construida exitosamente"
else
    print_error "Error al construir imagen"
    exit 1
fi

# PASO 5: Iniciar servicios
print_header "🚀 PASO 5: Iniciar servicios"

print_info "Iniciando servicios en segundo plano..."
if docker compose -f docker-compose.prod.yml up -d; then
    print_success "Servicios iniciados"
else
    print_error "Error al iniciar servicios"
    print_info "Ver logs: docker compose -f docker-compose.prod.yml logs"
    exit 1
fi

# Esperar a que los servicios estén listos
print_info "Esperando a que los servicios estén listos..."
sleep 10

# PASO 6: Verificar estado
print_header "✅ PASO 6: Verificar estado"

print_info "Estado de los contenedores:"
docker compose -f docker-compose.prod.yml ps

echo ""
print_info "Verificando health check..."
sleep 5

if curl -f http://localhost/health/ > /dev/null 2>&1; then
    print_success "Health check respondiendo correctamente"
else
    print_warning "Health check no responde aún (puede estar iniciándose)"
fi

# PASO 7: Mostrar logs recientes
print_header "📋 PASO 7: Logs recientes"

print_info "Últimas 20 líneas de logs:"
docker compose -f docker-compose.prod.yml logs --tail=20

# Resumen final
print_header "🎉 Despliegue Completado"

print_success "Servicios desplegados exitosamente"
echo ""
print_info "Accede a la aplicación en:"
echo "  • Página principal: http://localhost/"
echo "  • Admin:            http://localhost/admin/"
echo "  • Health check:     http://localhost/health/"
echo ""
print_info "Si configuraste un dominio:"
echo "  • https://certificados.transportespuno.gob.pe/"
echo ""
print_info "Comandos útiles:"
echo "  • Ver logs:    docker compose -f docker-compose.prod.yml logs -f"
echo "  • Ver estado:  docker compose -f docker-compose.prod.yml ps"
echo "  • Reiniciar:   docker compose -f docker-compose.prod.yml restart"
echo "  • Detener:     docker compose -f docker-compose.prod.yml stop"
echo ""

read -p "¿Ver logs en tiempo real? (s/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    print_info "Mostrando logs (Ctrl+C para salir)..."
    docker compose -f docker-compose.prod.yml logs -f
fi
