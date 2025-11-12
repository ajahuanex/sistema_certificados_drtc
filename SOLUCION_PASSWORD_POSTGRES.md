# 🔧 SOLUCIÓN: Error de Autenticación PostgreSQL

## Problema Detectado
```
FATAL: password authentication failed for user "certificados_user"
```

El servicio web no puede conectarse a PostgreSQL porque la contraseña no coincide.

## Causa
El volumen de PostgreSQL (`postgres_data_prod`) tiene datos de una instalación anterior con una contraseña diferente.

## Solución: Recrear PostgreSQL con Contraseña Correcta

### Paso 1: Detener todos los servicios
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production down
```

### Paso 2: Eliminar el volumen de PostgreSQL (ESTO BORRARÁ LOS DATOS)
```bash
docker volume rm sistema_certificados_drtc_postgres_data_prod
```

### Paso 3: Levantar los servicios nuevamente
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
```

### Paso 4: Verificar que todo funciona
```bash
# Ver estado de los servicios
docker compose -f docker-compose.prod.yml --env-file .env.production ps

# Ver logs del servicio web
docker compose -f docker-compose.prod.yml --env-file .env.production logs web --tail 50
```

### Paso 5: Ejecutar migraciones y crear superusuario
```bash
# Ejecutar migraciones
docker compose -f docker-compose.prod.yml --env-file .env.production exec web python manage.py migrate

# Crear superusuario
docker compose -f docker-compose.prod.yml --env-file .env.production exec web python manage.py create_superuser_if_not_exists
```

## Alternativa: Cambiar la Contraseña en PostgreSQL (Sin Perder Datos)

Si tienes datos importantes y NO quieres borrar el volumen:

### Paso 1: Conectarse al contenedor de PostgreSQL
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production exec db psql -U certificados_user -d certificados_prod
```

### Paso 2: Cambiar la contraseña (dentro de psql)
```sql
ALTER USER certificados_user WITH PASSWORD 'certificados_password_123';
\q
```

### Paso 3: Reiniciar el servicio web
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production restart web
```

## Verificación Final

Una vez aplicada la solución, verifica:

```bash
# Estado de servicios
docker compose -f docker-compose.prod.yml --env-file .env.production ps

# Logs del web (debe mostrar "Starting development server")
docker compose -f docker-compose.prod.yml --env-file .env.production logs web --tail 30

# Probar acceso
curl http://localhost:7070/health/
```

## Comandos Rápidos

```bash
# Detener todo
docker compose -f docker-compose.prod.yml --env-file .env.production down

# Eliminar volumen
docker volume rm sistema_certificados_drtc_postgres_data_prod

# Levantar todo
docker compose -f docker-compose.prod.yml --env-file .env.production up -d

# Ver logs
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f
```

---
**Nota:** Si eliges la opción de recrear el volumen, perderás todos los datos de la base de datos. Si tienes datos importantes, usa la alternativa de cambiar la contraseña.
