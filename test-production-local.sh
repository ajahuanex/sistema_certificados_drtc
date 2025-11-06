#!/bin/bash

echo "========================================"
echo "PRUEBA LOCAL DE CONFIGURACION PRODUCCION"
echo "========================================"
echo

echo "[1/6] Deteniendo contenedores existentes..."
docker-compose -f docker-compose.prod.yml down

echo
echo "[2/6] Limpiando redes Docker..."
docker network prune -f

echo
echo "[3/6] Construyendo imagen actualizada..."
docker-compose -f docker-compose.prod.yml build --no-cache web

echo
echo "[4/6] Iniciando servicios de produccion..."
docker-compose -f docker-compose.prod.yml up -d

echo
echo "[5/6] Esperando que los servicios esten listos..."
sleep 30

echo
echo "[6/6] Verificando estado de los contenedores..."
docker-compose -f docker-compose.prod.yml ps

echo
echo "========================================"
echo "VERIFICACION DE LOGS"
echo "========================================"
echo
echo "Logs del contenedor web:"
docker-compose -f docker-compose.prod.yml logs web

echo
echo "========================================"
echo "PRUEBA COMPLETADA"
echo "========================================"
echo
echo "Para acceder al sistema:"
echo "- URL: http://localhost"
echo "- Admin: http://localhost/admin/"
echo
echo "Para ver logs en tiempo real:"
echo "docker-compose -f docker-compose.prod.yml logs -f web"
echo