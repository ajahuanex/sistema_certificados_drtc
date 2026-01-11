# 🚨 SOLUCIÓN - PUERTO 7070 OCUPADO

## El Problema
Error: "Bind for 0.0.0.0:7070 failed: port is already allocated"
El puerto 7070 está siendo usado por otro proceso.

## Solución Inmediata

### 1. Encontrar qué está usando el puerto 7070
```bash
sudo netstat -tlnp | grep :7070
# o
sudo lsof -i :7070
```

### 2. Detener todos los contenedores Docker
```bash
# Detener todos los contenedores
docker stop $(docker ps -aq)

# Limpiar contenedores huérfanos
docker compose down --remove-orphans

# Limpiar redes no utilizadas
docker network prune -f
```

### 3. Verificar que el puerto esté libre
```bash
sudo netstat -tlnp | grep :7070
# No debería mostrar nada
```

### 4. Iniciar de nuevo
```bash
docker compose up -d

# Esperar y probar
sleep 20
curl -I http://localhost:7070/admin/
```

## Si el problema persiste

### Opción A: Usar otro puerto
```bash
# Cambiar a puerto 7071 en .env.production
sed -i 's/PORT=7070/PORT=7071/' .env.production

# Actualizar docker-compose.yml
sed -i 's/7070:8000/7071:8000/' docker-compose.yml

# Reiniciar
docker compose up -d
```

### Opción B: Matar el proceso que usa 7070
```bash
# Encontrar el PID del proceso
sudo lsof -i :7070

# Matar el proceso (reemplazar PID con el número real)
sudo kill -9 PID
```