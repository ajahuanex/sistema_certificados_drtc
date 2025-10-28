#!/bin/bash

# Script de Backup para Base de Datos PostgreSQL
# Sistema de Certificados DRTC Puno
#
# Este script crea backups de la base de datos PostgreSQL
# y los almacena con timestamp para fácil recuperación
#
# Uso:
#   ./backup_database.sh                    # Backup manual
#   ./backup_database.sh --restore <file>   # Restaurar desde backup
#
# Para backups automáticos, agregar a crontab:
#   0 2 * * * /var/www/certificates/backup_database.sh >> /var/log/backup-certificates.log 2>&1

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Función para imprimir mensajes
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Configuración
PROJECT_DIR="/var/www/certificates"
BACKUP_DIR="$PROJECT_DIR/backups"
ENV_FILE="$PROJECT_DIR/.env"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=30  # Mantener backups por 30 días

# Cargar variables de entorno
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' $ENV_FILE | xargs)
else
    print_error "No se encontró el archivo .env en $PROJECT_DIR"
    exit 1
fi

# Crear directorio de backups si no existe
mkdir -p $BACKUP_DIR

# Función para crear backup
create_backup() {
    print_message "Iniciando backup de base de datos..."
    
    BACKUP_FILE="$BACKUP_DIR/backup_${DB_NAME}_${TIMESTAMP}.sql"
    BACKUP_FILE_GZ="${BACKUP_FILE}.gz"
    
    # Crear backup usando pg_dump
    print_message "Exportando base de datos $DB_NAME..."
    PGPASSWORD=$DB_PASSWORD pg_dump \
        -h $DB_HOST \
        -p $DB_PORT \
        -U $DB_USER \
        -d $DB_NAME \
        -F p \
        --no-owner \
        --no-acl \
        -f $BACKUP_FILE
    
    if [ $? -eq 0 ]; then
        print_message "✓ Backup creado exitosamente: $BACKUP_FILE"
        
        # Comprimir backup
        print_message "Comprimiendo backup..."
        gzip $BACKUP_FILE
        
        if [ $? -eq 0 ]; then
            print_message "✓ Backup comprimido: $BACKUP_FILE_GZ"
            
            # Mostrar tamaño del archivo
            SIZE=$(du -h $BACKUP_FILE_GZ | cut -f1)
            print_message "Tamaño del backup: $SIZE"
        else
            print_error "Error al comprimir backup"
            exit 1
        fi
    else
        print_error "Error al crear backup"
        exit 1
    fi
    
    # Backup de archivos media (certificados y QR codes)
    print_message "Creando backup de archivos media..."
    MEDIA_BACKUP="$BACKUP_DIR/media_backup_${TIMESTAMP}.tar.gz"
    tar -czf $MEDIA_BACKUP -C $PROJECT_DIR media/
    
    if [ $? -eq 0 ]; then
        MEDIA_SIZE=$(du -h $MEDIA_BACKUP | cut -f1)
        print_message "✓ Backup de media creado: $MEDIA_BACKUP (Tamaño: $MEDIA_SIZE)"
    else
        print_warning "Error al crear backup de archivos media"
    fi
    
    # Limpiar backups antiguos
    print_message "Limpiando backups antiguos (más de $RETENTION_DAYS días)..."
    find $BACKUP_DIR -name "backup_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
    find $BACKUP_DIR -name "media_backup_*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete
    
    print_message "=========================================="
    print_message "Backup completado exitosamente!"
    print_message "=========================================="
    print_message "Backup de BD: $BACKUP_FILE_GZ"
    print_message "Backup de media: $MEDIA_BACKUP"
    echo ""
}

# Función para restaurar backup
restore_backup() {
    RESTORE_FILE=$1
    
    if [ ! -f "$RESTORE_FILE" ]; then
        print_error "Archivo de backup no encontrado: $RESTORE_FILE"
        exit 1
    fi
    
    print_warning "=========================================="
    print_warning "ADVERTENCIA: Restaurar backup"
    print_warning "=========================================="
    print_warning "Esta operación sobrescribirá la base de datos actual"
    print_warning "Base de datos: $DB_NAME"
    print_warning "Archivo: $RESTORE_FILE"
    echo ""
    read -p "¿Estás seguro de continuar? (escribir 'SI' para confirmar): " -r
    
    if [ "$REPLY" != "SI" ]; then
        print_message "Operación cancelada"
        exit 0
    fi
    
    print_message "Iniciando restauración..."
    
    # Descomprimir si es necesario
    if [[ $RESTORE_FILE == *.gz ]]; then
        print_message "Descomprimiendo backup..."
        TEMP_FILE="${RESTORE_FILE%.gz}"
        gunzip -c $RESTORE_FILE > $TEMP_FILE
        RESTORE_FILE=$TEMP_FILE
    fi
    
    # Crear backup de seguridad antes de restaurar
    print_message "Creando backup de seguridad antes de restaurar..."
    SAFETY_BACKUP="$BACKUP_DIR/safety_backup_${TIMESTAMP}.sql"
    PGPASSWORD=$DB_PASSWORD pg_dump \
        -h $DB_HOST \
        -p $DB_PORT \
        -U $DB_USER \
        -d $DB_NAME \
        -F p \
        -f $SAFETY_BACKUP
    gzip $SAFETY_BACKUP
    print_message "✓ Backup de seguridad creado: ${SAFETY_BACKUP}.gz"
    
    # Restaurar base de datos
    print_message "Restaurando base de datos..."
    PGPASSWORD=$DB_PASSWORD psql \
        -h $DB_HOST \
        -p $DB_PORT \
        -U $DB_USER \
        -d $DB_NAME \
        -f $RESTORE_FILE
    
    if [ $? -eq 0 ]; then
        print_message "✓ Base de datos restaurada exitosamente"
        
        # Limpiar archivo temporal si se descomprimió
        if [[ $1 == *.gz ]]; then
            rm -f $TEMP_FILE
        fi
    else
        print_error "Error al restaurar base de datos"
        print_warning "Puedes restaurar el backup de seguridad: ${SAFETY_BACKUP}.gz"
        exit 1
    fi
    
    print_message "=========================================="
    print_message "Restauración completada!"
    print_message "=========================================="
}

# Función para listar backups
list_backups() {
    print_message "Backups disponibles en $BACKUP_DIR:"
    echo ""
    echo "Base de datos:"
    ls -lh $BACKUP_DIR/backup_*.sql.gz 2>/dev/null || echo "  No hay backups de base de datos"
    echo ""
    echo "Archivos media:"
    ls -lh $BACKUP_DIR/media_backup_*.tar.gz 2>/dev/null || echo "  No hay backups de media"
    echo ""
}

# Procesar argumentos
case "$1" in
    --restore)
        if [ -z "$2" ]; then
            print_error "Debes especificar el archivo de backup a restaurar"
            echo "Uso: $0 --restore <archivo_backup>"
            exit 1
        fi
        restore_backup "$2"
        ;;
    --list)
        list_backups
        ;;
    --help)
        echo "Script de Backup - Sistema de Certificados DRTC Puno"
        echo ""
        echo "Uso:"
        echo "  $0                      Crear backup"
        echo "  $0 --restore <file>     Restaurar desde backup"
        echo "  $0 --list               Listar backups disponibles"
        echo "  $0 --help               Mostrar esta ayuda"
        echo ""
        ;;
    *)
        create_backup
        ;;
esac
