#!/bin/bash

# 🔄 Script de Rollback Manual para Producción
# Sistema de Certificados DRTC

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuración
APP_DIR="/app"
BACKUP_DIR="$APP_DIR/backups"
LOG_FILE="$APP_DIR/logs/rollback.log"
COMPOSE_FILE="docker-compose.prod.yml"

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

# Listar commits disponibles
list_commits() {
    print_step "Commits recientes disponibles:"
    echo ""
    git log --oneline -10
    echo ""
}

# Listar backups disponibles
list_backups() {
    print_step "Backups disponibles:"
    echo ""
    
    if [ -d "$BACKUP_DIR" ]; then
        ls -lh "$BACKUP_DIR"/*.sql.gz 2>/dev/null || echo "No hay backups disponibles"
    else
        echo "Directorio de backups no existe"
    fi
    echo ""
}

# Restaurar a un commit específico
rollback_to_commit() {
    local target_commit="$1"
    
    print_step "Revirtiendo a commit: $target_commit"
    
    # Verificar que el commit existe
    if ! git cat-file -e "$target_commit^{commit}" 2>/dev/null; then
        print_error "Commit no válido: $target_commit"
        return 1
    fi
    
    # Guardar commit actual
    local current_commit=$(git rev-parse HEAD)
    print_step "Commit actual: $current_commit"
    
    # Revertir código
    if git reset --hard "$target_commit"; then
        print_success "Código revertido a: $target_commit"
    else
        print_error "Error revirtiendo código"
        return 1
    fi
    
    # Reconstruir y reiniciar servicios
    print_step "Reconstruyendo servicios..."
    docker-compose -f "$COMPOSE_FILE" down
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Ejecutar migraciones
    print_step "Ejecutando migraciones..."
    sleep 10
    docker-compose -f "$COMPOSE_FILE" exec -T web python manage.py migrate
    
    # Recopilar estáticos
    print_step "Recopilando archivos estáticos..."
    docker-compose -f "$COMPOSE_FILE" exec -T web python manage.py collectstatic --noinput
    
    print_success "Rollback de código completado"
}

# Restaurar backup de base de datos
restore_database() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        print_error "Archivo de backup no encontrado: $backup_file"
        return 1
    fi
    
    print_step "Restaurando base de datos desde: $(basename "$backup_file")"
    
    # Crear backup de seguridad antes de restaurar
    print_step "Creando backup de seguridad..."
    local safety_backup="$BACKUP_DIR/safety_backup_$(date +%Y%m%d_%H%M%S).sql"
    docker-compose -f "$COMPOSE_FILE" exec -T db pg_dump -U certificados_user certificados_prod > "$safety_backup"
    gzip "$safety_backup"
    print_success "Backup de seguridad creado: $(basename "$safety_backup").gz"
    
    # Descomprimir si es necesario
    local sql_file="$backup_file"
    if [[ "$backup_file" == *.gz ]]; then
        print_step "Descomprimiendo backup..."
        gunzip -c "$backup_file" > "${backup_file%.gz}"
        sql_file="${backup_file%.gz}"
    fi
    
    # Detener aplicación web
    print_step "Deteniendo aplicación web..."
    docker-compose -f "$COMPOSE_FILE" stop web nginx
    
    # Restaurar base de datos
    print_step "Restaurando base de datos..."
    if docker-compose -f "$COMPOSE_FILE" exec -T db psql -U certificados_user certificados_prod < "$sql_file"; then
        print_success "Base de datos restaurada correctamente"
        
        # Limpiar archivo temporal
        if [[ "$backup_file" == *.gz ]]; then
            rm -f "$sql_file"
        fi
    else
        print_error "Error restaurando base de datos"
        print_warning "Puede restaurar el backup de seguridad: $(basename "$safety_backup").gz"
        return 1
    fi
    
    # Reiniciar servicios
    print_step "Reiniciando servicios..."
    docker-compose -f "$COMPOSE_FILE" start web nginx
    
    print_success "Restauración de base de datos completada"
}

# Verificar estado del sistema
check_system_status() {
    print_step "Verificando estado del sistema..."
    
    # Verificar servicios
    echo ""
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    
    # Verificar health check
    sleep 5
    if curl -f -s http://localhost/health/ > /dev/null 2>&1; then
        print_success "Sistema funcionando correctamente"
    else
        print_warning "Endpoint de salud no responde"
    fi
}

# Rollback completo (código + base de datos)
full_rollback() {
    local target_commit="$1"
    local backup_file="$2"
    
    print_step "=========================================="
    print_step "ROLLBACK COMPLETO"
    print_step "=========================================="
    
    # Rollback de código
    if [ -n "$target_commit" ]; then
        rollback_to_commit "$target_commit"
    else
        print_warning "No se especificó commit, saltando rollback de código"
    fi
    
    # Rollback de base de datos
    if [ -n "$backup_file" ]; then
        restore_database "$backup_file"
    else
        print_warning "No se especificó backup, saltando rollback de base de datos"
    fi
    
    # Verificar estado
    check_system_status
    
    print_success "=========================================="
    print_success "ROLLBACK COMPLETO FINALIZADO"
    print_success "=========================================="
}

# Menú interactivo
show_menu() {
    echo -e "${BLUE}=========================================="
    echo "🔄 Sistema de Rollback Manual"
    echo "   DRTC Certificados"
    echo "==========================================${NC}"
    echo ""
    echo "1. Ver commits recientes"
    echo "2. Ver backups disponibles"
    echo "3. Rollback a commit específico"
    echo "4. Restaurar backup de base de datos"
    echo "5. Rollback completo (código + BD)"
    echo "6. Verificar estado del sistema"
    echo "7. Rollback rápido (último commit + último backup)"
    echo "0. Salir"
    echo ""
    echo -n "Seleccione una opción: "
}

# Rollback rápido
quick_rollback() {
    print_step "=========================================="
    print_step "ROLLBACK RÁPIDO"
    print_step "=========================================="
    
    # Obtener último commit
    local previous_commit=$(git rev-parse HEAD~1)
    print_step "Revirtiendo a commit anterior: $previous_commit"
    
    # Obtener último backup
    local latest_backup=$(ls -t "$BACKUP_DIR"/*.sql.gz 2>/dev/null | head -1)
    
    if [ -z "$latest_backup" ]; then
        print_warning "No se encontró backup reciente"
        echo -n "¿Continuar solo con rollback de código? (y/N): "
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_warning "Rollback cancelado"
            return 1
        fi
    else
        print_step "Usando backup: $(basename "$latest_backup")"
    fi
    
    echo ""
    echo -e "${YELLOW}¿Está seguro que desea continuar? (y/N): ${NC}"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        full_rollback "$previous_commit" "$latest_backup"
    else
        print_warning "Rollback cancelado"
    fi
}

# Función principal
main() {
    # Cambiar al directorio de la aplicación
    cd "$APP_DIR" || exit 1
    
    # Crear directorio de logs si no existe
    mkdir -p "$(dirname "$LOG_FILE")"
    
    log "Iniciando script de rollback manual"
    
    # Si se pasan argumentos, ejecutar directamente
    if [ $# -gt 0 ]; then
        case "$1" in
            --commit)
                rollback_to_commit "$2"
                ;;
            --backup)
                restore_database "$2"
                ;;
            --full)
                full_rollback "$2" "$3"
                ;;
            --quick)
                quick_rollback
                ;;
            --status)
                check_system_status
                ;;
            *)
                echo "Uso: $0 [--commit HASH] [--backup FILE] [--full HASH FILE] [--quick] [--status]"
                exit 1
                ;;
        esac
        exit 0
    fi
    
    # Menú interactivo
    while true; do
        show_menu
        read -r option
        
        case $option in
            1)
                list_commits
                ;;
            2)
                list_backups
                ;;
            3)
                echo -n "Ingrese el hash del commit: "
                read -r commit_hash
                rollback_to_commit "$commit_hash"
                ;;
            4)
                echo -n "Ingrese la ruta del backup: "
                read -r backup_path
                restore_database "$backup_path"
                ;;
            5)
                echo -n "Ingrese el hash del commit: "
                read -r commit_hash
                echo -n "Ingrese la ruta del backup: "
                read -r backup_path
                full_rollback "$commit_hash" "$backup_path"
                ;;
            6)
                check_system_status
                ;;
            7)
                quick_rollback
                ;;
            0)
                print_success "Saliendo..."
                exit 0
                ;;
            *)
                print_error "Opción inválida"
                ;;
        esac
        
        echo ""
        echo "Presione Enter para continuar..."
        read -r
        clear
    done
}

# Manejo de señales
trap 'print_error "Script interrumpido"; exit 1' INT TERM

# Ejecutar función principal
main "$@"
