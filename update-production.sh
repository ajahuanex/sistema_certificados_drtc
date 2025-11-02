#!/bin/bash

# 🚀 Script de Actualización Automática para Producción
# Sistema de Certificados DRTC

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
APP_DIR="/app"
BACKUP_DIR="$APP_DIR/backups"
LOG_FILE="$APP_DIR/logs/update.log"
COMPOSE_FILE="docker-compose.prod.yml"
MAX_BACKUPS=7

# Funciones de utilidad
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

print_step() {
    echo -e "${BLUE}🔄 $1${NC}"
    log "STEP: $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    log "SUCCESS: $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    log "WARNING: $1"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    log "ERROR: $1"
}

# Verificar prerrequisitos
check_prerequisites() {
    print_step "Verificando prerrequisitos..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose no está instalado"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        print_error "Git no está instalado"
        exit 1
    fi
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "Archivo $COMPOSE_FILE no encontrado"
        exit 1
    fi
    
    print_success "Prerrequisitos verificados"
}

# Crear backup de la base de datos
create_backup() {
    print_step "Creando backup de la base de datos..."
    
    # Crear directorio de backup si no existe
    mkdir -p "$BACKUP_DIR"
    
    # Nombre del archivo de backup
    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
    
    # Crear backup
    if docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump -U certificados_user certificados_prod > "$BACKUP_FILE"; then
        print_success "Backup creado: $(basename "$BACKUP_FILE")"
        
        # Comprimir backup
        gzip "$BACKUP_FILE"
        print_success "Backup comprimido: $(basename "$BACKUP_FILE").gz"
        
        # Limpiar backups antiguos
        find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +$MAX_BACKUPS -delete
        print_success "Backups antiguos limpiados (>$MAX_BACKUPS días)"
    else
        print_error "Error creando backup"
        exit 1
    fi
}

# Verificar si hay actualizaciones
check_updates() {
    print_step "Verificando actualizaciones en GitHub..."
    
    # Fetch cambios remotos
    git fetch origin
    
    # Verificar si hay cambios
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main)
    
    if [ "$LOCAL" = "$REMOTE" ]; then
        print_success "El código ya está actualizado"
        return 1
    else
        print_success "Nuevas actualizaciones disponibles"
        
        # Mostrar cambios
        echo -e "${BLUE}📋 Cambios a aplicar:${NC}"
        git log --oneline "$LOCAL..$REMOTE"
        return 0
    fi
}

# Actualizar código desde GitHub
update_code() {
    print_step "Actualizando código desde GitHub..."
    
    # Guardar cambios locales si los hay
    if ! git diff-index --quiet HEAD --; then
        print_warning "Hay cambios locales, creando stash..."
        git stash push -m "Auto-stash before update $(date)"
    fi
    
    # Pull cambios
    if git pull origin main; then
        print_success "Código actualizado desde GitHub"
    else
        print_error "Error actualizando código"
        exit 1
    fi
}

# Verificar salud de los servicios
check_health() {
    print_step "Verificando salud de los servicios..."
    
    # Esperar a que los servicios estén listos
    sleep 10
    
    # Verificar cada servicio
    services=("db" "redis" "web" "nginx")
    
    for service in "${services[@]}"; do
        if docker-compose -f "$COMPOSE_FILE" ps "$service" | grep -q "Up"; then
            print_success "Servicio $service: OK"
        else
            print_error "Servicio $service: FALLO"
            return 1
        fi
    done
    
    # Verificar endpoint de salud
    sleep 5
    if curl -f -s http://localhost/health/ > /dev/null; then
        print_success "Endpoint de salud: OK"
    else
        print_warning "Endpoint de salud no responde (puede ser normal durante el inicio)"
        # Intentar una vez más después de esperar
        sleep 10
        if curl -f -s http://localhost/health/ > /dev/null; then
            print_success "Endpoint de salud: OK (segundo intento)"
        else
            print_error "Endpoint de salud: FALLO"
            return 1
        fi
    fi
}

# Actualizar servicios Docker
update_services() {
    print_step "Actualizando servicios Docker..."
    
    # Detener servicios
    print_step "Deteniendo servicios..."
    docker-compose -f "$COMPOSE_FILE" down
    
    # Reconstruir imágenes
    print_step "Reconstruyendo imágenes..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    # Iniciar servicios
    print_step "Iniciando servicios..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    print_success "Servicios Docker actualizados"
}

# Ejecutar migraciones de base de datos
run_migrations() {
    print_step "Ejecutando migraciones de base de datos..."
    
    # Esperar a que la base de datos esté lista
    sleep 5
    
    if docker-compose -f "$COMPOSE_FILE" exec -T web python manage.py migrate; then
        print_success "Migraciones ejecutadas correctamente"
    else
        print_error "Error ejecutando migraciones"
        exit 1
    fi
}

# Recopilar archivos estáticos
collect_static() {
    print_step "Recopilando archivos estáticos..."
    
    if docker-compose -f "$COMPOSE_FILE" exec -T web python manage.py collectstatic --noinput; then
        print_success "Archivos estáticos recopilados"
    else
        print_error "Error recopilando archivos estáticos"
        exit 1
    fi
}

# Limpiar sistema Docker
cleanup_docker() {
    print_step "Limpiando sistema Docker..."
    
    # Limpiar imágenes no utilizadas
    docker image prune -f
    
    # Limpiar volúmenes no utilizados
    docker volume prune -f
    
    print_success "Sistema Docker limpiado"
}

# Función de rollback
rollback() {
    print_error "Iniciando rollback..."
    
    # Volver al commit anterior
    git reset --hard HEAD~1
    
    # Reiniciar servicios
    docker-compose -f "$COMPOSE_FILE" down
    docker-compose -f "$COMPOSE_FILE" up -d --build
    
    print_warning "Rollback completado. Revise los logs para más detalles."
}

# Enviar notificación (opcional)
send_notification() {
    local status="$1"
    local message="$2"
    
    # Aquí puedes agregar integración con Slack, email, etc.
    # Ejemplo con curl para webhook:
    # curl -X POST -H 'Content-type: application/json' \
    #   --data "{\"text\":\"$message\"}" \
    #   "$SLACK_WEBHOOK_URL"
    
    log "NOTIFICATION: $status - $message"
}

# Función principal
main() {
    echo -e "${BLUE}🚀 Sistema de Actualización Automática - DRTC Certificados${NC}"
    echo "================================================="
    
    # Cambiar al directorio de la aplicación
    cd "$APP_DIR" || exit 1
    
    # Crear directorio de logs si no existe
    mkdir -p "$(dirname "$LOG_FILE")"
    
    log "Iniciando proceso de actualización"
    
    # Verificar prerrequisitos
    check_prerequisites
    
    # Verificar si hay actualizaciones
    if ! check_updates; then
        print_success "No hay actualizaciones disponibles"
        exit 0
    fi
    
    # Crear backup antes de actualizar
    create_backup
    
    # Actualizar código
    update_code
    
    # Actualizar servicios
    update_services
    
    # Ejecutar migraciones
    run_migrations
    
    # Recopilar archivos estáticos
    collect_static
    
    # Verificar salud del sistema
    if check_health; then
        print_success "✅ Actualización completada exitosamente"
        send_notification "SUCCESS" "Sistema actualizado correctamente"
        
        # Limpiar Docker
        cleanup_docker
        
        log "Actualización completada exitosamente"
    else
        print_error "❌ Problemas detectados después de la actualización"
        send_notification "WARNING" "Actualización completada pero con advertencias"
        
        echo -e "${YELLOW}¿Desea hacer rollback? (y/N)${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            rollback
        fi
    fi
}

# Manejo de señales
trap 'print_error "Script interrumpido"; exit 1' INT TERM

# Verificar si se ejecuta como root (opcional)
if [[ $EUID -eq 0 ]]; then
    print_warning "Ejecutándose como root. Se recomienda usar un usuario específico."
fi

# Ejecutar función principal
main "$@"