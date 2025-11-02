#!/bin/bash
# Script de inicio rápido para Docker

set -e

echo "🐳 Sistema de Certificados DRTC Puno - Inicio Rápido"
echo "=================================================="
echo ""

# Verificar que Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    echo "Instala Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar que Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    echo "Instala Docker Compose desde: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker y Docker Compose están instalados"
echo ""

# Verificar si existe .env
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
    
    # Generar SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" 2>/dev/null || openssl rand -base64 50)
    
    # Reemplazar en .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/tu-clave-secreta-super-segura-cambiala-en-produccion/$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/tu-clave-secreta-super-segura-cambiala-en-produccion/$SECRET_KEY/" .env
    fi
    
    echo "✅ Archivo .env creado con SECRET_KEY generada"
    echo ""
    echo "⚠️  IMPORTANTE: Edita .env y cambia los passwords antes de producción"
    echo ""
fi

# Construir imágenes
echo "🔨 Construyendo imágenes Docker..."
docker-compose build

echo ""
echo "🚀 Levantando servicios..."
docker-compose up -d

echo ""
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Verificar estado
echo ""
echo "📊 Estado de los servicios:"
docker-compose ps

echo ""
echo "✅ ¡Sistema listo!"
echo ""
echo "🌐 Accede a la aplicación en: http://localhost"
echo "👤 Usuario por defecto: admin"
echo "🔑 Password: admin123 (cámbialo en producción)"
echo ""
echo "📝 Comandos útiles:"
echo "  - Ver logs: docker-compose logs -f"
echo "  - Detener: docker-compose stop"
echo "  - Reiniciar: docker-compose restart"
echo "  - Eliminar todo: docker-compose down -v"
echo ""
echo "📚 Documentación completa en: DOCKER_DEPLOYMENT.md"
echo ""
