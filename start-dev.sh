#!/bin/bash

# 🚀 Script de Inicio Rápido para Desarrollo
# Sistema de Certificados DRTC

echo "🚀 Iniciando Sistema de Certificados DRTC - Desarrollo"
echo "=================================================="

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    exit 1
fi

echo "✅ Docker y Docker Compose disponibles"

# Crear directorios necesarios
echo "📁 Creando directorios necesarios..."
mkdir -p media staticfiles logs backups

# Construir y levantar servicios
echo "🔨 Construyendo imágenes..."
docker-compose build

echo "🚀 Levantando servicios..."
docker-compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Ejecutar migraciones
echo "🗄️  Ejecutando migraciones..."
docker-compose exec web python manage.py migrate

# Recopilar archivos estáticos
echo "📦 Recopilando archivos estáticos..."
docker-compose exec web python manage.py collectstatic --noinput

# Crear superusuario si no existe
echo "👤 Configurando superusuario..."
docker-compose exec web python manage.py create_superuser_if_not_exists

# Cargar plantilla por defecto
echo "📄 Cargando plantilla por defecto..."
docker-compose exec web python manage.py load_default_template

echo ""
echo "✅ ¡Sistema iniciado correctamente!"
echo ""
echo "🌐 Aplicación disponible en: http://localhost:8000"
echo "🔧 Panel de administración: http://localhost:8000/admin/"
echo "🗄️  Adminer (BD): http://localhost:8080"
echo ""
echo "📊 Para ver logs en tiempo real:"
echo "   docker-compose logs -f web"
echo ""
echo "🛑 Para detener el sistema:"
echo "   docker-compose down"
echo ""
echo "🔄 Para reiniciar un servicio:"
echo "   docker-compose restart web"
echo ""

# Mostrar estado de los servicios
echo "📋 Estado de los servicios:"
docker-compose ps