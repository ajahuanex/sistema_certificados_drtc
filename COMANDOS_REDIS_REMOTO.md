# Comandos para Solucionar Redis en Servidor Remoto

## Opción 1: Script Automático

```bash
# 1. Crear el script de corrección
cat > fix-redis-remoto.sh << 'EOF'
#!/bin/bash
echo "=== Solucionando Redis ==="
docker compose -f docker-compose.prod.yml down
docker volume rm $(basename $(pwd))_redis_data_prod 2>/dev/null || true

# Actualizar docker-compose.prod.yml
cp docker-compose.prod.yml docker-compose.prod.yml.backup
sed -i 's/command: >/command: redis-server --requirepass ${REDIS_PASSWORD:-redis_password}/' docker-compose.prod.yml
sed -i 's/test: \["CMD", "redis-cli", "ping"\]/test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD:-redis_password}", "ping"]/' docker-compose.prod.yml

# Verificar REDIS_URL
if ! grep -q "REDIS_URL=redis://:.*@redis:6379/0" .env.production; then
    sed -i 's|REDIS_URL=redis://redis:6379/0|REDIS_URL=redis://:redis_password@redis:6379/0|g' .env.production
fi

docker compose -f docker-compose.prod.yml up -d
sleep 30
docker compose -f docker-compose.prod.yml exec redis redis-cli -a redis_password ping
EOF

chmod +x fix-redis-remoto.sh
./fix-redis-remoto.sh
```

## Opción 2: Comandos Manuales

```bash
# 1. Detener servicios
docker compose -f docker-compose.prod.yml down

# 2. Limpiar volumen de Redis
docker volume rm $(basename $(pwd))_redis_data_prod

# 3. Actualizar docker-compose.prod.yml
cp docker-compose.prod.yml docker-compose.prod.yml.backup

# 4. Editar la sección de Redis (reemplazar toda la sección redis)
nano docker-compose.prod.yml
```

**En el editor, reemplazar la sección redis con:**

```yaml
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
```

```bash
# 5. Verificar .env.production
grep REDIS_URL .env.production

# Si no tiene la contraseña, actualizar:
sed -i 's|REDIS_URL=redis://redis:6379/0|REDIS_URL=redis://:redis_password@redis:6379/0|g' .env.production

# 6. Iniciar servicios
docker compose -f docker-compose.prod.yml up -d

# 7. Esperar y verificar
sleep 30
docker compose -f docker-compose.prod.yml exec redis redis-cli -a redis_password ping

# 8. Ver estado
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs web --tail=10
```

## Verificación Final

```bash
# Verificar que Redis responde
docker compose -f docker-compose.prod.yml exec redis redis-cli -a redis_password ping
# Debe responder: PONG

# Verificar aplicación web
curl -I http://localhost:7070/admin/
# Debe responder: HTTP/1.1 200 OK (o 302 redirect)

# Ver logs en tiempo real
docker compose -f docker-compose.prod.yml logs web -f
```

## Si hay problemas

```bash
# Ver logs detallados
docker compose -f docker-compose.prod.yml logs redis
docker compose -f docker-compose.prod.yml logs web

# Reiniciar solo el servicio web
docker compose -f docker-compose.prod.yml restart web

# Verificar configuración
cat .env.production | grep REDIS
```