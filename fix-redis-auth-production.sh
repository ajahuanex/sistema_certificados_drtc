#!/bin/bash

echo "=== Solucionando problema de autenticación Redis ==="
echo ""

echo "1. Deteniendo servicios..."
docker compose -f docker-compose.prod.yml down

echo ""
echo "2. Eliminando volumen de Redis para limpiar datos sin contraseña..."
docker volume rm sistema_certificados_drtc_redis_data_prod 2>/dev/null || echo "Volumen no existía"

echo ""
echo "3. Iniciando servicios con Redis configurado con contraseña..."
docker compose -f docker-compose.prod.yml up -d

echo ""
echo "4. Esperando que los servicios estén listos..."
sleep 30

echo ""
echo "5. Verificando Redis con autenticación..."
docker compose -f docker-compose.prod.yml exec redis redis-cli -a redis_password ping

echo ""
echo "6. Verificando estado de los servicios..."
docker compose -f docker-compose.prod.yml ps

echo ""
echo "7. Verificando logs del servicio web (últimas 10 líneas)..."
docker compose -f docker-compose.prod.yml logs web --tail=10

echo ""
echo "=== Corrección completada ==="
echo "Si Redis responde 'PONG', la autenticación está funcionando correctamente."
echo "Puedes acceder a la aplicación en: http://localhost:7070"