# 🚀 Guía Completa de Despliegue a Producción

## 📋 Índice
1. [Solución al Error Actual](#solución-al-error-actual)
2. [Pre-requisitos](#pre-requisitos)
3. [Configuración Inicial](#configuración-inicial)
4. [Despliegue Paso a Paso](#despliegue-paso-a-paso)
5. [Verificación](#verificación)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Solución al Error Actual

### Error: "permission denied: /app/entrypoint.sh"

**Causa:** El archivo `entrypoint.sh` no tiene permisos de ejecución en Windows.

**Solución Rápida:**

```cmd
REM 1. Detener contenedores actuales
docker-compose -f docker-compose.prod.yml down

REM 2. Dar permisos de ejecución al entrypoint.sh
git update-index --chmod=+x entrypoint.sh

REM 3. Reconstruir la imagen
docker-compose -f docker-compose.prod.yml build --no-cache web

REM 4. Iniciar de nuevo
docker-compose -f docker-compose.prod.yml up -d
```

**Solución Alternativa (si la anterior no funciona):**

Editar el `Dockerfile` para asegurar permisos:

```dockerfile
# Agregar después de copiar entrypoint.sh
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh
```

---

## 📋 Pre-requisitos

### Software Necesario
- ✅ Docker Desktop instalado y corriendo
- ✅ Git instalado
- ✅ Acceso a terminal (CMD o PowerShell)

### Archivos Necesarios
- ✅ `.env.production` configurado
- ✅ `docker-compose.prod.yml` presente
- ✅ Certificados SSL (opcional para HTTPS)

### Verificar Docker
```cmd
docker --version
docker-compose --version
docker ps
```

---

## ⚙️ Configuración Inicial

### 1. Configurar Variables de Entorno

Copia y edita el archivo de producción:

```cmd
copy .env.production.example .env.production
```

Edita `.env.production` con tus valores:

```env
# Django
SECRET_KEY=tu-clave-secreta-muy-segura-aqui-cambiar
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,tu-dominio.com

# Base de datos
DB_ENGINE=django.db.backends.postgresql
DB_NAME=certificados_prod
DB_USER=certificados_user
DB_PASSWORD=tu-password-seguro-aqui
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Superusuario
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@tudominio.com
DJANGO_SUPERUSER_PASSWORD=tu-password-admin-seguro

# Email (opcional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-email
```

### 2. Verificar Archivos de Configuración

```cmd
REM Verificar que existen los archivos necesarios
dir docker-compose.prod.yml
dir .env.production
dir Dockerfile
dir entrypoint.sh
dir nginx.prod.conf
```

---

## 🚀 Despliegue Paso a Paso

### Paso 1: Limpiar Ambiente Anterior (si existe)

```cmd
REM Detener y eliminar contenedores anteriores
docker-compose -f docker-compose.prod.yml down -v

REM Limpiar imágenes antiguas (opcional)
docker system prune -f
```

### Paso 2: Dar Permisos al Entrypoint

```cmd
REM Opción 1: Usando Git
git update-index --chmod=+x entrypoint.sh

REM Opción 2: Verificar en Dockerfile que tenga:
REM RUN chmod +x /app/entrypoint.sh
```

### Paso 3: Construir Imágenes

```cmd
REM Construir todas las imágenes
docker-compose -f docker-compose.prod.yml build --no-cache

REM O construir solo el servicio web
docker-compose -f docker-compose.prod.yml build --no-cache web
```

### Paso 4: Iniciar Servicios

```cmd
REM Iniciar todos los servicios en segundo plano
docker-compose -f docker-compose.prod.yml up -d

REM Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f
```

### Paso 5: Verificar Estado de Servicios

```cmd
REM Ver estado de contenedores
docker-compose -f docker-compose.prod.yml ps

REM Verificar logs de cada servicio
docker-compose -f docker-compose.prod.yml logs db
docker-compose -f docker-compose.prod.yml logs redis
docker-compose -f docker-compose.prod.yml logs web
docker-compose -f docker-compose.prod.yml logs nginx
```

### Paso 6: Verificar Health Checks

```cmd
REM Esperar 30 segundos para que los servicios estén listos
timeout /t 30

REM Verificar health check
curl http://localhost/health/

REM O abrir en navegador
start http://localhost/health/
```

---

## ✅ Verificación

### 1. Verificar Servicios Corriendo

```cmd
docker-compose -f docker-compose.prod.yml ps
```

Deberías ver algo como:
```
NAME                          STATUS              PORTS
certificados_db_prod          Up (healthy)        5432/tcp
certificados_redis_prod       Up (healthy)        6379/tcp
certificados_web_prod         Up                  8000/tcp
certificados_nginx_prod       Up                  0.0.0.0:80->80/tcp
```

### 2. Verificar Acceso Web

Abre tu navegador y visita:

- **Página principal:** http://localhost/
- **Admin:** http://localhost/admin/
- **Health check:** http://localhost/health/
- **API:** http://localhost/api/

### 3. Verificar Base de Datos

```cmd
REM Conectar a PostgreSQL
docker-compose -f docker-compose.prod.yml exec db psql -U certificados_user -d certificados_prod

REM Dentro de psql:
\dt  -- Listar tablas
\q   -- Salir
```

### 4. Verificar Redis

```cmd
REM Conectar a Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli

REM Dentro de redis-cli:
PING  -- Debería responder PONG
KEYS *  -- Ver todas las claves
exit
```

### 5. Verificar Logs

```cmd
REM Ver logs de todos los servicios
docker-compose -f docker-compose.prod.yml logs --tail=50

REM Ver logs de un servicio específico
docker-compose -f docker-compose.prod.yml logs web --tail=50
```

---

## 🔍 Troubleshooting

### Error: "permission denied: /app/entrypoint.sh"

**Solución:**
```cmd
docker-compose -f docker-compose.prod.yml down
git update-index --chmod=+x entrypoint.sh
docker-compose -f docker-compose.prod.yml build --no-cache web
docker-compose -f docker-compose.prod.yml up -d
```

### Error: "port is already allocated"

**Causa:** El puerto 80 ya está en uso.

**Solución:**
```cmd
REM Ver qué está usando el puerto 80
netstat -ano | findstr :80

REM Cambiar puerto en docker-compose.prod.yml
REM nginx:
REM   ports:
REM     - "8080:80"  # Cambiar de 80 a 8080
```

### Error: "database does not exist"

**Solución:**
```cmd
REM Recrear la base de datos
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d db
timeout /t 10
docker-compose -f docker-compose.prod.yml up -d
```

### Error: "connection refused" a PostgreSQL

**Solución:**
```cmd
REM Verificar que PostgreSQL está corriendo
docker-compose -f docker-compose.prod.yml ps db

REM Ver logs de PostgreSQL
docker-compose -f docker-compose.prod.yml logs db

REM Reiniciar servicio
docker-compose -f docker-compose.prod.yml restart db
```

### Error: "connection refused" a Redis

**Solución:**
```cmd
REM Verificar que Redis está corriendo
docker-compose -f docker-compose.prod.yml ps redis

REM Ver logs de Redis
docker-compose -f docker-compose.prod.yml logs redis

REM Reiniciar servicio
docker-compose -f docker-compose.prod.yml restart redis
```

### Contenedor se reinicia constantemente

**Diagnóstico:**
```cmd
REM Ver logs del contenedor
docker-compose -f docker-compose.prod.yml logs web

REM Ver últimas 100 líneas
docker-compose -f docker-compose.prod.yml logs web --tail=100
```

**Causas comunes:**
1. Error en migraciones
2. Error en variables de entorno
3. Error en conexión a base de datos
4. Error en código Python

### Limpiar y Empezar de Nuevo

```cmd
REM Detener todo
docker-compose -f docker-compose.prod.yml down -v

REM Limpiar volúmenes
docker volume prune -f

REM Limpiar imágenes
docker image prune -a -f

REM Reconstruir desde cero
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📊 Comandos Útiles de Producción

### Gestión de Servicios

```cmd
REM Iniciar servicios
docker-compose -f docker-compose.prod.yml up -d

REM Detener servicios
docker-compose -f docker-compose.prod.yml stop

REM Reiniciar servicios
docker-compose -f docker-compose.prod.yml restart

REM Detener y eliminar
docker-compose -f docker-compose.prod.yml down

REM Detener y eliminar con volúmenes
docker-compose -f docker-compose.prod.yml down -v
```

### Ver Logs

```cmd
REM Logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f

REM Logs de un servicio
docker-compose -f docker-compose.prod.yml logs web -f

REM Últimas 50 líneas
docker-compose -f docker-compose.prod.yml logs --tail=50
```

### Ejecutar Comandos Django

```cmd
REM Ejecutar migraciones
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

REM Crear superusuario
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

REM Recopilar estáticos
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

REM Shell de Django
docker-compose -f docker-compose.prod.yml exec web python manage.py shell

REM Ejecutar comando personalizado
docker-compose -f docker-compose.prod.yml exec web python manage.py tu_comando
```

### Backup y Restore

```cmd
REM Backup de base de datos
docker-compose -f docker-compose.prod.yml exec db pg_dump -U certificados_user certificados_prod > backup.sql

REM Restore de base de datos
docker-compose -f docker-compose.prod.yml exec -T db psql -U certificados_user certificados_prod < backup.sql

REM Backup de archivos media
docker cp certificados_web_prod:/app/media ./media_backup

REM Restore de archivos media
docker cp ./media_backup certificados_web_prod:/app/media
```

### Monitoreo

```cmd
REM Ver uso de recursos
docker stats

REM Ver procesos en un contenedor
docker-compose -f docker-compose.prod.yml exec web ps aux

REM Ver espacio en disco
docker system df

REM Inspeccionar contenedor
docker-compose -f docker-compose.prod.yml exec web df -h
```

---

## 🔐 Seguridad en Producción

### Checklist de Seguridad

- [ ] `DEBUG=False` en `.env.production`
- [ ] `SECRET_KEY` único y seguro
- [ ] Contraseñas fuertes para DB y admin
- [ ] `ALLOWED_HOSTS` configurado correctamente
- [ ] Certificados SSL configurados (HTTPS)
- [ ] Firewall configurado
- [ ] Backups automáticos configurados
- [ ] Logs monitoreados
- [ ] Actualizaciones de seguridad aplicadas

### Generar SECRET_KEY Seguro

```python
# Ejecutar en Python
import secrets
print(secrets.token_urlsafe(50))
```

O usar:
```cmd
docker-compose -f docker-compose.prod.yml exec web python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 📈 Monitoreo y Mantenimiento

### Health Checks Automáticos

```cmd
REM Verificar health check cada 5 minutos
REM Crear un script check-health.bat:

@echo off
:loop
curl -f http://localhost/health/ || echo "Health check failed!"
timeout /t 300
goto loop
```

### Logs Rotativos

Los logs de Docker se rotan automáticamente, pero puedes configurar:

En `docker-compose.prod.yml`:
```yaml
services:
  web:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Backup Automático

Crear script `backup-daily.bat`:
```cmd
@echo off
set BACKUP_DIR=backups\%date:~-4,4%%date:~-10,2%%date:~-7,2%
mkdir %BACKUP_DIR%

REM Backup de base de datos
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U certificados_user certificados_prod > %BACKUP_DIR%\database.sql

REM Backup de media
docker cp certificados_web_prod:/app/media %BACKUP_DIR%\media

echo Backup completado en %BACKUP_DIR%
```

---

## 🎯 Checklist Final de Despliegue

### Antes de Desplegar
- [ ] `.env.production` configurado
- [ ] `SECRET_KEY` generado y único
- [ ] Contraseñas seguras configuradas
- [ ] `ALLOWED_HOSTS` correcto
- [ ] Permisos de `entrypoint.sh` correctos
- [ ] Docker Desktop corriendo

### Durante el Despliegue
- [ ] Imágenes construidas sin errores
- [ ] Servicios iniciados correctamente
- [ ] Health checks pasando
- [ ] Migraciones ejecutadas
- [ ] Archivos estáticos recopilados
- [ ] Superusuario creado

### Después del Despliegue
- [ ] Acceso web funcionando
- [ ] Admin accesible
- [ ] Base de datos conectada
- [ ] Redis funcionando
- [ ] Logs sin errores críticos
- [ ] Backup configurado
- [ ] Monitoreo activo

---

## 📞 Soporte

Si encuentras problemas:

1. **Revisa los logs:**
   ```cmd
   docker-compose -f docker-compose.prod.yml logs --tail=100
   ```

2. **Verifica el estado:**
   ```cmd
   docker-compose -f docker-compose.prod.yml ps
   ```

3. **Consulta la documentación:**
   - `docs/PRODUCTION_DEPLOYMENT.md`
   - `COMANDOS_RAPIDOS_PRODUCCION.md`
   - `GUIA_PRODUCCION_PASO_A_PASO.md`

---

**¡Listo para producción! 🚀**
