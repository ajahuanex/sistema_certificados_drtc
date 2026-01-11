#!/bin/bash

# Script de despliegue para servidor 161.132.47.99
# Sistema de Certificados DRTC - Producción
# Usuario: administrador (Docker ya instalado)

SERVER_IP="161.132.47.99"
SERVER_USER="administrador"
PROJECT_DIR="/home/administrador/sistema_certificados_drtc"
REPO_URL="https://github.com/ajahuanex/sistema_certificados_drtc.git"

echo "🚀 INICIANDO DESPLIEGUE EN SERVIDOR $SERVER_IP"
echo "Usuario: $SERVER_USER"
echo "Directorio: $PROJECT_DIR"
echo "================================================"

# Función para ejecutar comandos en el servidor remoto
run_remote() {
    echo "📡 Ejecutando en servidor: $1"
    ssh $SERVER_USER@$SERVER_IP "$1"
}

# Función para copiar archivos al servidor
copy_to_server() {
    echo "📁 Copiando $1 al servidor..."
    scp "$1" $SERVER_USER@$SERVER_IP:"$2"
}

echo "1️⃣ Verificando conexión al servidor..."
if ! ping -c 1 $SERVER_IP > /dev/null 2>&1; then
    echo "❌ Error: No se puede conectar al servidor $SERVER_IP"
    exit 1
fi

echo "✅ Conexión al servidor OK"

echo "2️⃣ Verificando Docker (ya instalado)..."
run_remote "docker --version && docker-compose --version"

echo "3️⃣ Creando directorio del proyecto..."
run_remote "mkdir -p $PROJECT_DIR"

echo "4️⃣ Clonando/actualizando repositorio..."
run_remote "cd $PROJECT_DIR && git clone $REPO_URL . 2>/dev/null || git pull origin main"

echo "5️⃣ Copiando archivos de configuración..."
copy_to_server ".env.production" "$PROJECT_DIR/.env.production"
copy_to_server "docker-compose.prod.yml" "$PROJECT_DIR/docker-compose.prod.yml"

echo "6️⃣ Configurando permisos..."
run_remote "cd $PROJECT_DIR && chmod +x entrypoint.sh"

echo "7️⃣ Deteniendo servicios anteriores (si existen)..."
run_remote "cd $PROJECT_DIR && docker-compose -f docker-compose.prod.yml down 2>/dev/null || true"

echo "8️⃣ Construyendo contenedores..."
run_remote "cd $PROJECT_DIR && docker-compose -f docker-compose.prod.yml build"

echo "9️⃣ Iniciando servicios..."
run_remote "cd $PROJECT_DIR && docker-compose -f docker-compose.prod.yml up -d"

echo "🔟 Esperando que los servicios se inicien..."
sleep 30

echo "1️⃣1️⃣ Ejecutando migraciones..."
run_remote "cd $PROJECT_DIR && docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate"

echo "1️⃣2️⃣ Creando superusuario..."
run_remote "cd $PROJECT_DIR && docker-compose -f docker-compose.prod.yml exec -T web python manage.py create_superuser_if_not_exists"

echo "1️⃣3️⃣ Cargando plantilla por defecto..."
run_remote "cd $PROJECT_DIR && docker-compose -f docker-compose.prod.yml exec -T web python manage.py load_default_template"

echo "1️⃣4️⃣ Verificando estado de servicios..."
run_remote "cd $PROJECT_DIR && docker-compose -f docker-compose.prod.yml ps"

echo "✅ DESPLIEGUE COMPLETADO"
echo "========================"
echo "🌐 Aplicación disponible en: http://$SERVER_IP:7070"
echo "🔧 Admin disponible en: http://$SERVER_IP:7070/admin"
echo "📊 Dashboard disponible en: http://$SERVER_IP:7070/admin/dashboard"
echo ""
echo "Credenciales por defecto:"
echo "Usuario: admin"
echo "Contraseña: admin123"