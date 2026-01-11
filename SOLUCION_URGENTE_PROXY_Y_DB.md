# 🚨 SOLUCIÓN URGENTE - PROXY Y BASE DE DATOS

## Lo que pasó
1. `docker network prune -f` eliminó las redes del proxy inverso
2. Django no puede conectar a PostgreSQL (busca `db` pero se llama `postgres`)

## PASO 1: Arreglar el proxy inverso
```bash
cd ~/dockers/nginx-proxy

# Limpiar y recrear
docker compose down
docker compose up -d

# Verificar que funcione
docker compose ps
```

## PASO 2: Arreglar la base de datos en certificados
```bash
cd ~/dockers/sistema_certificados_drtc

# Ver la configuración actual
grep -E "DB_HOST|POSTGRES_HOST" .env.production

# Corregir el host (cambiar db por postgres)
sed -i 's/DB_HOST=db/DB_HOST=postgres/' .env.production
sed -i 's/POSTGRES_HOST=db/POSTGRES_HOST=postgres/' .env.production

# Verificar el cambio
grep -E "DB_HOST|POSTGRES_HOST" .env.production

# Reiniciar solo el contenedor web
docker compose restart web

# Ver los logs
docker compose logs web --tail=10
```

## PASO 3: Probar todo
```bash
# Probar la aplicación directamente
curl -I http://localhost:7070/admin/

# Probar a través del proxy
curl -I https://certificados.transportespuno.gob.pe/admin/
```

## Si el proxy sigue fallando
```bash
cd ~/dockers/nginx-proxy

# Ver logs del proxy
docker compose logs

# Recrear completamente
docker compose down --volumes
docker compose up -d
```