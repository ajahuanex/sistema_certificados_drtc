#!/bin/bash
# Script de prueba completa para producción - Linux/Mac
# Sistema de Certificados DRTC

set -e  # Salir si hay algún error

echo "========================================"
echo "PRUEBA COMPLETA DE PRODUCCION"
echo "Sistema de Certificados DRTC"
echo "========================================"
echo ""

# Verificar que Docker está instalado
echo "[1/8] Verificando Docker..."
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker no está instalado"
    echo "Por favor instala Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "OK: Docker instalado"
echo ""

# Detener contenedores existentes
echo "[2/8] Deteniendo contenedores existentes..."
docker compose -f docker-compose.prod.yml down || true
echo ""

# Limpiar red si existe
echo "[3/8] Limpiando redes Docker..."
docker network prune -f
echo ""

# Construir imágenes sin cache
echo "[4/8] Construyendo imagen Docker (esto puede tardar varios minutos)..."
docker compose -f docker-compose.prod.yml build --no-cache
echo "OK: Imagen construida exitosamente"
echo ""

# Iniciar servicios
echo "[5/8] Iniciando servicios..."
docker compose -f docker-compose.prod.yml up -d
echo "OK: Servicios iniciados"
echo ""

# Esperar a que los servicios estén listos
echo "[6/8] Esperando a que los servicios estén listos (30 segundos)..."
sleep 30
echo ""

# Verificar estado de contenedores
echo "[7/8] Verificando estado de contenedores..."
docker compose -f docker-compose.prod.yml ps
echo ""

# Verificar logs del contenedor web
echo "[8/8] Verificando logs del contenedor web..."
echo ""
echo "=== ULTIMAS 50 LINEAS DE LOGS ==="
docker compose -f docker-compose.prod.yml logs --tail=50 web
echo ""

echo "========================================"
echo "PRUEBA COMPLETADA"
echo "========================================"
echo ""
echo "Verifica que todos los contenedores estén 'Up' y 'healthy'"
echo ""
echo "Accede a la aplicación en:"
echo "  - http://localhost (Aplicación principal)"
echo "  - http://localhost/admin/ (Panel de administración)"
echo ""
echo "Para ver logs en tiempo real:"
echo "  docker compose -f docker-compose.prod.yml logs -f web"
echo ""
echo "Para detener los servicios:"
echo "  docker compose -f docker-compose.prod.yml down"
echo ""
