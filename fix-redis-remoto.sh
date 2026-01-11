#!/bin/bash

echo "=== Solucionando Redis en servidor remoto ==="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "Error: No se encuentra docker-compose.prod.yml"
    echo "Asegúrate de estar en el directorio del proyecto"
    exit 1
fi

echo "1. Deteniendo servicios..."
docker compose -f docker-compose.prod.yml down

echo ""
echo "2. Eliminando volumen de Redis para limpiar datos sin contraseña..."
docker volume rm $(basename $(pwd))_redis_data_prod 2>/dev/null || echo "Volumen no existía"

echo ""
echo "3. Actualizando docker-compose.prod.yml para Redis con contraseña..."

# Crear backup del archivo original
cp docker-compose.prod.yml docker-compose.prod.yml.backup

# Actualizar la configuración de Redis
sed -i '/redis:/,/healthcheck:/c\
  redis:\
    image: redis:7-alpine\
    container_name: certificados_redis_prod\
    restart: unless-stopped\
    command: >\
      redis-server\
      --requirepass ${REDIS_PASSWORD:-redis_password}\
      --appendonly yes\
      --maxmemory 512mb\
      --maxmemory-policy allkeys-lru\
      --save 900 1\
      --save 300 10\
      --save 60 10000\
    volumes:\
      - redis_data_prod:/data\
    networks:\
      - certificados_network\
    healthcheck:\
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD:-redis_password}", "ping"]\
      interval: 30s\
      timeout: 10s\
      retries: 3' docker-compose.prod.yml

echo ""
echo "4. Verificando configuración de Redis en .env.production..."
if grep -q "REDIS_URL=redis://:.*@redis:6379/0" .env.production; then
    echo "✓ REDIS_URL ya está configurado correctamente"
else
    echo "Actualizando REDIS_URL..."
    sed -i 's|REDIS_URL=redis://redis:6379/0|REDIS_URL=redis://:redis_password@redis:6379/0|g' .env.production
fi

echo ""
echo "5. Iniciando servicios con Redis configurado..."
docker compose -f docker-compose.prod.yml up -d

echo ""
echo "6. Esperando que los servicios estén listos..."
sleep 45

echo ""
echo "7. Verificando Redis con autenticación..."
docker compose -f docker-compose.prod.yml exec redis redis-cli -a redis_password ping

echo ""
echo "8. Verificando estado de los servicios..."
docker compose -f docker-compose.prod.yml ps

echo ""
echo "9. Verificando logs del servicio web (últimas 5 líneas)..."
docker compose -f docker-compose.prod.yml logs web --tail=5

echo ""
echo "=== Corrección completada ==="
echo ""
echo "Si Redis responde 'PONG', la autenticación está funcionando."
echo "Puedes verificar la aplicación en: http://$(hostname -I | awk '{print $1}'):7070"
echo ""
echo "Para monitorear logs en tiempo real:"
echo "docker compose -f docker-compose.prod.yml logs web -f"