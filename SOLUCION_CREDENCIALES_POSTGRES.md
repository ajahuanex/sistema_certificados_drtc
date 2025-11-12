# 🔧 Solución: Credenciales de PostgreSQL

## 🔍 Problema Identificado
```
psycopg2.OperationalError: password authentication failed for user "certificados_user"
```

El volumen de PostgreSQL tiene credenciales diferentes a las del `.env.production`.

## ✅ Solución: Recrear Base de Datos

### Comandos a Ejecutar:

```bash
# 1. Detener todos los contenedores
docker compose -f docker-compose.prod.yml --env-file .env.production down

# 2. Eliminar el volumen de PostgreSQL
docker volume rm sistema_certificados_drtc_postgres_data_prod

# 3. Iniciar de nuevo (creará la BD con las credenciales correctas)
docker compose -f docker-compose.prod.yml --env-file .env.production up -d

# 4. Esperar 30 segundos para que inicien los servicios
sleep 30

# 5. Ver el estado de los servicios
docker compose -f docker-compose.prod.yml --env-file .env.production ps

# 6. Ver los logs del servicio web
docker compose -f docker-compose.prod.yml --env-file .env.production logs web
```

## 📋 Credenciales Configuradas

Según `.env.production`:
- **Usuario**: certificados_user
- **Password**: certificados_password_123
- **Base de datos**: certificados_prod
- **Host**: db
- **Puerto**: 5432

## ⚠️ Nota Importante

Este proceso eliminará cualquier dato existente en la base de datos. Como estamos en fase de pruebas, no hay problema.

## 🎯 Resultado Esperado

Después de ejecutar estos comandos, deberías ver:
- ✅ PostgreSQL: healthy
- ✅ Redis: healthy
- ✅ Web: healthy
- ✅ Nginx: healthy

## 🔄 Si Persiste el Error

Si después de esto sigue fallando, verifica:
1. Que el archivo `.env.production` tenga las credenciales correctas
2. Que no haya espacios extra en las variables de entorno
3. Los logs completos: `docker compose -f docker-compose.prod.yml --env-file .env.production logs`
