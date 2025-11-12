#!/bin/bash
# Script para corregir permisos de directorios en producción

echo "========================================"
echo "Corrigiendo permisos de directorios"
echo "========================================"
echo ""

echo "[1/5] Deteniendo contenedores..."
docker compose -f docker-compose.prod.yml --env-file .env.production down

echo ""
echo "[2/5] Corrigiendo permisos de directorios..."
sudo chown -R $USER:$USER staticfiles media logs backups 2>/dev/null || true
sudo chmod -R 755 staticfiles media logs backups 2>/dev/null || true

echo ""
echo "[3/5] Creando directorios si no existen..."
mkdir -p staticfiles media logs backups

echo ""
echo "[4/5] Iniciando contenedores..."
docker compose -f docker-compose.prod.yml --env-file .env.production up -d

echo ""
echo "[5/5] Esperando 30 segundos para que inicien los servicios..."
sleep 30

echo ""
echo "========================================"
echo "Verificando estado de los servicios"
echo "========================================"
docker compose -f docker-compose.prod.yml --env-file .env.production ps

echo ""
echo "Para ver los logs:"
echo "docker compose -f docker-compose.prod.yml --env-file .env.production logs -f web"
