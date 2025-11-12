#!/bin/bash
# Script para corregir credenciales de PostgreSQL en Ubuntu

echo "========================================"
echo "Corrigiendo credenciales de PostgreSQL"
echo "========================================"
echo ""

echo "[1/6] Listando volúmenes de Docker..."
docker volume ls | grep postgres

echo ""
echo "[2/6] Deteniendo contenedores..."
docker compose -f docker-compose.prod.yml --env-file .env.production down

echo ""
echo "[3/6] Identificando y eliminando volumen de PostgreSQL..."
VOLUME_NAME=$(docker volume ls -q | grep postgres | grep -E '(prod|sistema_certificados)')
if [ -z "$VOLUME_NAME" ]; then
    echo "No se encontró volumen de PostgreSQL, buscando todos los volúmenes..."
    docker volume ls
    echo ""
    echo "Por favor, identifica el volumen correcto y ejecútalo manualmente:"
    echo "docker volume rm <nombre_del_volumen>"
else
    echo "Eliminando volumen: $VOLUME_NAME"
    docker volume rm $VOLUME_NAME
    if [ $? -eq 0 ]; then
        echo "✓ Volumen eliminado exitosamente"
    else
        echo "✗ Error al eliminar volumen"
    fi
fi

echo ""
echo "[4/6] Recreando contenedores..."
docker compose -f docker-compose.prod.yml --env-file .env.production up -d

echo ""
echo "[5/6] Esperando a que los servicios inicien (30 segundos)..."
sleep 30

echo ""
echo "[6/6] Verificando estado de los servicios..."
docker compose -f docker-compose.prod.yml --env-file .env.production ps

echo ""
echo "========================================"
echo "Proceso completado"
echo "========================================"
echo ""
echo "Verifica los logs con:"
echo "docker compose -f docker-compose.prod.yml --env-file .env.production logs web"
echo ""
