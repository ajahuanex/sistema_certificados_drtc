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
ROLLBACK_ENABLED=true
AUTO_ROLLBACK=true
HEALTH_CHECK_RETRIES=3
HEALTH_CHECK_DELAY=10

# Variables de estado
CURRENT_COMMIT=""
PREVIOUS_COMMIT=""
BACKUP_FILE=""
DEPLOYMENT_FAILED=false

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
        BACKUP_FILE="${BACKUP_FILE}.gz"
        print_success "Backup comprimido: $(basename "$BACKUP_FILE")"
        
        # Limpiar backups antiguos
        find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +$MAX_BACKUPS -delete
        print_success "Backups antiguos limpiados (>$MAX_BACKUPS días)"
    else
        print_error "Error creando backup"
        exit 1
    fi
}

# Restaurar backup de la base de datos
restore_backup() {
    local backup_file="$1"
    
    print_step "Restaurando backup de la base de datos..."
    
    if [ ! -f "$backup_file" ]; then
        print_error "Archivo de backup no encontrado: $backup_file"
        return 1
    fi
    
    # Descomprimir si es necesario
    local sql_file="$backup_file"
    if [[ "$backup_file" == *.gz ]]; then
        print_step "Descomprimiendo backup..."
        gunzip -c "$backup_file" > "${backup_file%.gz}"
        sql_file="${backup_file%.gz}"
    fi
    
    # Restaurar base de datos
    print_step "Restaurando base de datos desde backup..."
    if docker-compose -f "$COMPOSE_FILE" exec -T db psql -U certificados_user certificados_prod < "$sql_file"; then
        print_success "Base de datos restaurada correctamente"
        
        # Limpiar archivo temporal si se descomprimió
        if [[ "$backup_file" == *.gz ]]; then
            rm -f "$sql_file"
        fi
        
        return 0
    else
        print_error "Error restaurando base de datos"
        return 1
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
    
    local retry_count=0
    local max_retries=$HEALTH_CHECK_RETRIES
    
    # Esperar a que los servicios estén listos
    sleep "$HEALTH_CHECK_DELAY"
    
    while [ $retry_count -lt $max_retries ]; do
        local all_healthy=true
        
        # Verificar cada servicio
        services=("db" "redis" "web" "nginx")
        
        for service in "${services[@]}"; do
            if docker-compose -f "$COMPOSE_FILE" ps "$service" | grep -q "Up"; then
                print_success "Servicio $service: OK"
            else
                print_error "Servicio $service: FALLO"
                all_healthy=false
            fi
        done
        
        # Verificar endpoint de salud
        if curl -f -s http://localhost/health/ > /dev/null 2>&1; then
            print_success "Endpoint de salud: OK"
        else
            print_warning "Endpoint de salud no responde"
            all_healthy=false
        fi
        
        # Si todo está saludable, retornar éxito
        if [ "$all_healthy" = true ]; then
            print_success "Todos los servicios están saludables"
            return 0
        fi
        
        # Incrementar contador e intentar de nuevo
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $max_retries ]; then
            print_warning "Intento $retry_count/$max_retries falló. Reintentando en ${HEALTH_CHECK_DELAY}s..."
            sleep "$HEALTH_CHECK_DELAY"
        fi
    done
    
    print_error "Health check falló después de $max_retries intentos"
    return 1
}

# Verificar integridad de la aplicación
check_application_integrity() {
    print_step "Verificando integridad de la aplicación..."
    
    local checks_passed=true
    
    # Verificar que Django puede importar settings
    if docker-compose -f "$COMPOSE_FILE" exec -T web python -c "from django.conf import settings; print(settings.DEBUG)" > /dev/null 2>&1; then
        print_success "Configuración de Django: OK"
    else
        print_error "Configuración de Django: FALLO"
        checks_passed=false
    fi
    
    # Verificar conexión a base de datos
    if docker-compose -f "$COMPOSE_FILE" exec -T web python manage.py check --database default > /dev/null 2>&1; then
        print_success "Conexión a base de datos: OK"
    else
        print_error "Conexión a base de datos: FALLO"
        checks_passed=false
    fi
    
    # Verificar que no hay migraciones pendientes
    if docker-compose -f "$COMPOSE_FILE" exec -T web python manage.py showmigrations --plan | grep -q "\[ \]"; then
        print_warning "Hay migraciones pendientes"
    else
        print_success "Migraciones: OK"
    fi
    
    # Verificar logs de errores recientes
    if docker-compose -f "$COMPOSE_FILE" logs --tail=50 web 2>&1 | grep -qi "error\|exception\|traceback"; then
        print_warning "Se detectaron errores en los logs recientes"
        checks_passed=false
    else
        print_success "Logs de aplicación: OK"
    fi
    
    if [ "$checks_passed" = true ]; then
        return 0
    else
        return 1
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

# Función de rollback automático
perform_rollback() {
    local reason="$1"
    
    print_error "=========================================="
    print_error "INICIANDO ROLLBACK AUTOMÁTICO"
    print_error "Razón: $reason"
    print_error "=========================================="
    
    DEPLOYMENT_FAILED=true
    
    # Paso 1: Volver al commit anterior
    print_step "Revirtiendo código al commit anterior..."
    if [ -n "$PREVIOUS_COMMIT" ]; then
        if git reset --hard "$PREVIOUS_COMMIT"; then
            print_success "Código revertido a commit: $PREVIOUS_COMMIT"
        else
            print_error "Error revirtiendo código"
        fi
    else
        print_warning "No se pudo identificar el commit anterior"
    fi
    
    # Paso 2: Detener servicios actuales
    print_step "Deteniendo servicios..."
    docker-compose -f "$COMPOSE_FILE" down
    
    # Paso 3: Restaurar backup de base de datos
    if [ -n "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
        print_step "Restaurando backup de base de datos..."
        
        # Iniciar solo el servicio de base de datos
        docker-compose -f "$COMPOSE_FILE" up -d db
        sleep 10
        
        if restore_backup "$BACKUP_FILE"; then
            print_success "Base de datos restaurada correctamente"
        else
            print_error "Error restaurando base de datos"
            print_warning "Backup disponible en: $BACKUP_FILE"
        fi
    else
        print_warning "No hay backup disponible para restaurar"
    fi
    
    # Paso 4: Reconstruir y reiniciar servicios con versión anterior
    print_step "Reconstruyendo servicios con versión anterior..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Paso 5: Verificar que el rollback fue exitoso
    sleep 15
    print_step "Verificando estado después del rollback..."
    
    if check_health; then
        print_success "=========================================="
        print_success "ROLLBACK COMPLETADO EXITOSAMENTE"
        print_success "Sistema restaurado a versión anterior"
        print_success "=========================================="
        send_notification "ROLLBACK_SUCCESS" "Rollback completado exitosamente. Sistema restaurado."
        return 0
    else
        print_error "=========================================="
        print_error "ROLLBACK FALLÓ"
        print_error "Se requiere intervención manual"
        print_error "=========================================="
        send_notification "ROLLBACK_FAILED" "CRÍTICO: Rollback falló. Se requiere intervención manual inmediata."
        return 1
    fi
}

# Función de rollback manual
rollback_manual() {
    print_warning "Iniciando rollback manual..."
    
    echo -e "${YELLOW}¿Está seguro que desea hacer rollback? (y/N)${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        perform_rollback "Rollback manual solicitado por usuario"
    else
        print_warning "Rollback cancelado"
    fi
}

# Enviar notificación
send_notification() {
    local status="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    log "NOTIFICATION: $status - $message"
    
    # Crear archivo de notificación
    local notification_file="$APP_DIR/logs/notifications.log"
    echo "[$timestamp] $status: $message" >> "$notification_file"
    
    # Integración con Slack (si está configurado)
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        local color="good"
        case "$status" in
            "ERROR"|"ROLLBACK_FAILED")
                color="danger"
                ;;
            "WARNING"|"ROLLBACK_SUCCESS")
                color="warning"
                ;;
            "SUCCESS")
                color="good"
                ;;
        esac
        
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"attachments\":[{\"color\":\"$color\",\"title\":\"Despliegue DRTC\",\"text\":\"$message\",\"footer\":\"$timestamp\"}]}" \
            "$SLACK_WEBHOOK_URL" 2>/dev/null || true
    fi
    
    # Integración con email (si está configurado)
    if [ -n "$NOTIFICATION_EMAIL" ] && command -v mail &> /dev/null; then
        echo "$message" | mail -s "[$status] Despliegue DRTC - $timestamp" "$NOTIFICATION_EMAIL" 2>/dev/null || true
    fi
    
    # Integración con webhook personalizado (si está configurado)
    if [ -n "$WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"status\":\"$status\",\"message\":\"$message\",\"timestamp\":\"$timestamp\",\"commit\":\"$CURRENT_COMMIT\"}" \
            "$WEBHOOK_URL" 2>/dev/null || true
    fi
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
    send_notification "INFO" "Iniciando proceso de actualización"
    
    # Verificar prerrequisitos
    check_prerequisites
    
    # Guardar commit actual antes de actualizar
    PREVIOUS_COMMIT=$(git rev-parse HEAD)
    log "Commit actual: $PREVIOUS_COMMIT"
    
    # Verificar si hay actualizaciones
    if ! check_updates; then
        print_success "No hay actualizaciones disponibles"
        exit 0
    fi
    
    # Crear backup antes de actualizar
    create_backup
    
    # Actualizar código
    update_code
    
    # Guardar nuevo commit
    CURRENT_COMMIT=$(git rev-parse HEAD)
    log "Nuevo commit: $CURRENT_COMMIT"
    
    # Actualizar servicios
    if ! update_services; then
        print_error "Error actualizando servicios"
        if [ "$AUTO_ROLLBACK" = true ]; then
            perform_rollback "Error al actualizar servicios Docker"
            exit 1
        fi
    fi
    
    # Ejecutar migraciones
    if ! run_migrations; then
        print_error "Error ejecutando migraciones"
        if [ "$AUTO_ROLLBACK" = true ]; then
            perform_rollback "Error al ejecutar migraciones de base de datos"
            exit 1
        fi
    fi
    
    # Recopilar archivos estáticos
    if ! collect_static; then
        print_error "Error recopilando archivos estáticos"
        if [ "$AUTO_ROLLBACK" = true ]; then
            perform_rollback "Error al recopilar archivos estáticos"
            exit 1
        fi
    fi
    
    # Verificar salud del sistema
    print_step "Ejecutando verificaciones post-despliegue..."
    
    if ! check_health; then
        print_error "Health check falló"
        if [ "$AUTO_ROLLBACK" = true ]; then
            perform_rollback "Health check falló después de la actualización"
            exit 1
        else
            send_notification "ERROR" "Health check falló. Se requiere intervención manual."
            exit 1
        fi
    fi
    
    # Verificar integridad de la aplicación
    if ! check_application_integrity; then
        print_error "Verificación de integridad falló"
        if [ "$AUTO_ROLLBACK" = true ]; then
            perform_rollback "Verificación de integridad de la aplicación falló"
            exit 1
        else
            send_notification "ERROR" "Verificación de integridad falló. Se requiere intervención manual."
            exit 1
        fi
    fi
    
    # Si llegamos aquí, el despliegue fue exitoso
    print_success "=========================================="
    print_success "✅ ACTUALIZACIÓN COMPLETADA EXITOSAMENTE"
    print_success "=========================================="
    print_success "Commit anterior: $PREVIOUS_COMMIT"
    print_success "Commit actual: $CURRENT_COMMIT"
    print_success "Backup disponible: $(basename "$BACKUP_FILE")"
    
    send_notification "SUCCESS" "Sistema actualizado correctamente de $PREVIOUS_COMMIT a $CURRENT_COMMIT"
    
    # Limpiar Docker
    cleanup_docker
    
    log "Actualización completada exitosamente"
}

# Manejo de señales
trap 'print_error "Script interrumpido"; exit 1' INT TERM

# Verificar si se ejecuta como root (opcional)
if [[ $EUID -eq 0 ]]; then
    print_warning "Ejecutándose como root. Se recomienda usar un usuario específico."
fi

# Ejecutar función principal
main "$@"