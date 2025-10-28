#!/bin/bash

# Script de Deployment para Sistema de Certificados DRTC Puno
# Este script automatiza el proceso de deployment en producción

set -e  # Salir si hay algún error

echo "=========================================="
echo "Sistema de Certificados DRTC Puno"
echo "Script de Deployment"
echo "=========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables de configuración
PROJECT_DIR="/var/www/certificates"
VENV_DIR="$PROJECT_DIR/venv"
REPO_URL="https://github.com/your-org/certificates-drtc.git"  # Actualizar con tu repo
BRANCH="main"
PYTHON_VERSION="python3.10"

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

# Verificar que se ejecuta como root o con sudo
if [ "$EUID" -ne 0 ]; then 
    print_error "Este script debe ejecutarse como root o con sudo"
    exit 1
fi

# Verificar que existe el archivo .env
if [ ! -f "$PROJECT_DIR/.env" ]; then
    print_error "No se encontró el archivo .env en $PROJECT_DIR"
    print_warning "Copia .env.example a .env y configura las variables necesarias"
    exit 1
fi

print_message "Iniciando proceso de deployment..."

# 1. Actualizar código desde repositorio
print_message "Actualizando código desde repositorio..."
cd $PROJECT_DIR
if [ -d ".git" ]; then
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
else
    print_warning "No es un repositorio git. Saltando actualización de código."
fi

# 2. Activar entorno virtual
print_message "Activando entorno virtual..."
if [ ! -d "$VENV_DIR" ]; then
    print_message "Creando entorno virtual..."
    $PYTHON_VERSION -m venv $VENV_DIR
fi
source $VENV_DIR/bin/activate

# 3. Instalar/actualizar dependencias
print_message "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Ejecutar migraciones
print_message "Ejecutando migraciones de base de datos..."
python manage.py migrate --noinput

# 5. Recolectar archivos estáticos
print_message "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# 6. Crear superusuario si no existe
print_message "Verificando superusuario..."
python manage.py create_superuser_if_not_exists

# 7. Cargar plantilla por defecto si no existe
print_message "Verificando plantilla por defecto..."
python manage.py load_default_template

# 8. Verificar permisos de archivos
print_message "Configurando permisos de archivos..."
chown -R www-data:www-data $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
chmod -R 775 $PROJECT_DIR/media
chmod -R 775 $PROJECT_DIR/logs

# 9. Reiniciar servicios
print_message "Reiniciando servicios..."
systemctl restart certificates-drtc
systemctl restart nginx

# 10. Verificar estado de servicios
print_message "Verificando estado de servicios..."
if systemctl is-active --quiet certificates-drtc; then
    print_message "✓ Servicio certificates-drtc está activo"
else
    print_error "✗ Servicio certificates-drtc no está activo"
    systemctl status certificates-drtc
    exit 1
fi

if systemctl is-active --quiet nginx; then
    print_message "✓ Nginx está activo"
else
    print_error "✗ Nginx no está activo"
    systemctl status nginx
    exit 1
fi

# 11. Ejecutar tests (opcional)
read -p "¿Deseas ejecutar los tests? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    print_message "Ejecutando tests..."
    python manage.py test --keepdb
fi

echo ""
print_message "=========================================="
print_message "Deployment completado exitosamente!"
print_message "=========================================="
print_message "Aplicación disponible en: https://certificados.drtcpuno.gob.pe"
print_message "Panel de administración: https://certificados.drtcpuno.gob.pe/admin/"
echo ""
