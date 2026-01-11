#!/bin/bash

# Script para ejecutar en el servidor remoto via SSH
# Uso: ./ejecutar-en-remoto.sh IP_SERVIDOR

IP_SERVIDOR=${1:-"161.132.47.92"}
USUARIO="administrador"

echo "=== Conectando a $IP_SERVIDOR para solucionar Redis ==="

ssh -t $USUARIO@$IP_SERVIDOR << 'ENDSSH'
cd ~/dockers/sistema_certificados_drtc

echo "=== Solucionando problema Redis ==="
echo "Directorio actual: $(pwd)"

# Detener servicios
echo "1. Deteniendo servicios..."
docker compose -f docker-compose.prod.yml down

# Limpiar volumen Redis
echo "2. Limpiando volumen Redis..."
docker volume rm sistema_certificados_drtc_redis_data_prod 2>/dev/null || echo "Volumen no existía"

# Backup del archivo
echo "3. Creando backup..."
cp docker-compose.prod.yml docker-compose.prod.yml.backup.$(date +%Y%m%d_%H%M%S)

# Actualizar configuración Redis
echo "4. Actualizando configuración Redis..."
cat > temp_redis_config << 'EOF'
  redis:
    image: redis:7-alpine
    container_name: certificados_redis_prod
    restart: unless-stopped
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD:-redis_password}
      --appendonly yes
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
      --save 900 1
      --save 300 10
      --save 60 10000
    volumes:
      - redis_data_prod:/data
    networks:
      - certificados_network
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD:-redis_password}", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
EOF

# Reemplazar sección redis en docker-compose.prod.yml
python3 << 'EOFPYTHON'
import re

# Leer archivo
with open('docker-compose.prod.yml', 'r') as f:
    content = f.read()

# Leer nueva configuración
with open('temp_redis_config', 'r') as f:
    new_redis = f.read()

# Reemplazar sección redis
pattern = r'  redis:.*?(?=  \w+:|$)'
content = re.sub(pattern, new_redis, content, flags=re.DOTALL)

# Escribir archivo
with open('docker-compose.prod.yml', 'w') as f:
    f.write(content)
EOFPYTHON

rm temp_redis_config

# Verificar REDIS_URL
echo "5. Verificando REDIS_URL..."
if ! grep -q "REDIS_URL=redis://:.*@redis:6379/0" .env.production; then
    echo "Actualizando REDIS_URL..."
    sed -i 's|REDIS_URL=redis://redis:6379/0|REDIS_URL=redis://:redis_password@redis:6379/0|g' .env.production
fi

# Mostrar configuración actual
echo "6. Configuración Redis actual:"
grep -A 2 -B 2 REDIS .env.production

# Iniciar servicios
echo "7. Iniciando servicios..."
docker compose -f docker-compose.prod.yml up -d

# Esperar
echo "8. Esperando 45 segundos..."
sleep 45

# Verificar Redis
echo "9. Verificando Redis..."
docker compose -f docker-compose.prod.yml exec redis redis-cli -a redis_password ping

# Estado servicios
echo "10. Estado de servicios:"
docker compose -f docker-compose.prod.yml ps

# Logs recientes
echo "11. Logs recientes del web:"
docker compose -f docker-compose.prod.yml logs web --tail=5

echo ""
echo "=== Corrección completada ==="
echo "Aplicación disponible en: http://$(hostname -I | awk '{print $1}'):7070"

ENDSSH

echo ""
echo "=== Comando SSH completado ==="