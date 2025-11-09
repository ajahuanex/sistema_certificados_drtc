# Guía de Docker Compose - Sistema de Certificados DRTC

Esta guía explica la configuración de Docker Compose para los entornos de desarrollo y producción.

## Tabla de Contenidos

- [Arquitectura](#arquitectura)
- [Entorno de Desarrollo](#entorno-de-desarrollo)
- [Entorno de Producción](#entorno-de-producción)
- [Volúmenes Persistentes](#volúmenes-persistentes)
- [Health Checks](#health-checks)
- [Comandos Útiles](#comandos-útiles)
- [Troubleshooting](#troubleshooting)

## Arquitectura

El sistema utiliza una arquitectura de microservicios con los siguientes componentes:

### Servicios Comunes (Desarrollo y Producción)

1. **web**: Aplicación Django con Gunicorn
2. **db**: Base de datos PostgreSQL 15
3. **redis**: Cache y almacenamiento de sesiones

### Servicios Adicionales (Solo Producción)

4. **nginx**: Reverse proxy y servidor de archivos estáticos
5. **backup**: Servicio de backup automático (opcional)
6. **monitoring**: Monitoreo de recursos (opcional)

## Entorno de Desarrollo

### Características

- Hot-reload automático con Django runserver
- Base de datos PostgreSQL en contenedor
- Redis para cache y sesiones
- Adminer para administración de BD (opcional)
- Volúmenes montados para desarrollo en tiempo real

### Iniciar Entorno de Desarrollo

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f web
```

### Servicios Disponibles

- **Aplicación Django**: http://localhost:8000
- **Adminer (BD Admin)**: http://localhost:8080 (requiere profile admin)
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Iniciar con Adminer

```bash
docker-compose --profile admin up -d
```

### Configuración de Desarrollo

El archivo `docker-compose.yml` incluye:

- **Volúmenes de código**: Montaje del directorio actual para hot-reload
- **Variables de entorno**: Configuración de desarrollo con DEBUG=True
- **Puertos expuestos**: Acceso directo a todos los servicios
- **Health checks**: Verificación automática del estado de servicios

## Entorno de Producción

### Características

- Gunicorn con múltiples workers
- Nginx como reverse proxy
- SSL/HTTPS configurado
- Optimizaciones de PostgreSQL
- Redis con persistencia
- Backups automáticos
- Health checks robustos

### Iniciar Entorno de Producción

```bash
# Iniciar todos los servicios
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Verificar estado de servicios
docker-compose -f docker-compose.prod.yml ps
```

### Servicios Disponibles

- **Aplicación (vía Nginx)**: http://localhost:8181 (HTTP) y https://localhost:8443 (HTTPS)
- **Monitoreo**: http://localhost:9100 (requiere profile monitoring)

### Variables de Entorno

Crear archivo `.env.production` con las siguientes variables:

```bash
# Django
SECRET_KEY=tu_secret_key_super_seguro
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# Base de datos
DB_NAME=certificados_prod
DB_USER=certificados_user
DB_PASSWORD=tu_password_seguro
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password
```

### Servicios Opcionales

#### Backup Automático

```bash
# Iniciar servicio de backup
docker-compose -f docker-compose.prod.yml --profile backup up -d backup

# El servicio creará backups cada 24 horas automáticamente
# Los backups se guardan en ./backups/
```

#### Monitoreo

```bash
# Iniciar servicio de monitoreo
docker-compose -f docker-compose.prod.yml --profile monitoring up -d monitoring

# Acceder a métricas en http://localhost:9100
```

## Volúmenes Persistentes

### Desarrollo

- `postgres_data_dev`: Datos de PostgreSQL
- `redis_data_dev`: Datos de Redis
- `media_files`: Archivos media (certificados, QR codes)
- `static_files`: Archivos estáticos de Django

### Producción

- `postgres_data_prod`: Datos de PostgreSQL
- `redis_data_prod`: Datos de Redis
- `./media`: Archivos media (montaje directo)
- `./staticfiles`: Archivos estáticos (montaje directo)
- `./logs`: Logs de aplicación y Nginx
- `./backups`: Backups de base de datos

### Gestión de Volúmenes

```bash
# Listar volúmenes
docker volume ls

# Inspeccionar un volumen
docker volume inspect postgres_data_dev

# Eliminar volúmenes no utilizados
docker volume prune

# Backup manual de volumen
docker run --rm -v postgres_data_prod:/data -v $(pwd)/backups:/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

## Health Checks

Todos los servicios tienen health checks configurados para garantizar disponibilidad.

### Web (Django)

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### PostgreSQL

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U certificados_user -d certificados_prod"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Redis

```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Nginx

```yaml
healthcheck:
  test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health/"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Verificar Health Checks

```bash
# Ver estado de health checks
docker-compose ps

# Inspeccionar health check de un servicio
docker inspect --format='{{json .State.Health}}' certificados_web_prod | jq
```

## Comandos Útiles

### Gestión de Servicios

```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Reiniciar un servicio
docker-compose restart web

# Reconstruir imágenes
docker-compose build --no-cache

# Ver logs
docker-compose logs -f web

# Ejecutar comando en contenedor
docker-compose exec web python manage.py migrate
```

### Mantenimiento

```bash
# Limpiar contenedores detenidos
docker-compose down --remove-orphans

# Limpiar todo (incluyendo volúmenes)
docker-compose down -v

# Ver uso de recursos
docker stats

# Inspeccionar red
docker network inspect certificados_network
```

### Base de Datos

```bash
# Acceder a PostgreSQL
docker-compose exec db psql -U certificados_user -d certificados_dev

# Crear backup
docker-compose exec db pg_dump -U certificados_user certificados_dev > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U certificados_user -d certificados_dev < backup.sql

# Ver logs de PostgreSQL
docker-compose logs -f db
```

### Django

```bash
# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Recopilar archivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Ejecutar tests
docker-compose exec web python manage.py test

# Shell de Django
docker-compose exec web python manage.py shell
```

## Troubleshooting

### Problema: Servicios no inician

```bash
# Ver logs detallados
docker-compose logs

# Verificar configuración
docker-compose config

# Verificar estado de servicios
docker-compose ps
```

### Problema: Base de datos no conecta

```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps db

# Ver logs de PostgreSQL
docker-compose logs db

# Verificar health check
docker inspect certificados_db_dev | grep -A 10 Health
```

### Problema: Volúmenes con permisos incorrectos

```bash
# Cambiar propietario de volúmenes
docker-compose exec web chown -R app:app /app/media
docker-compose exec web chown -R app:app /app/staticfiles
```

### Problema: Puerto ya en uso

```bash
# Cambiar puerto en docker-compose.yml
# De:
ports:
  - "8000:8000"
# A:
ports:
  - "8001:8000"
```

### Problema: Contenedor se reinicia constantemente

```bash
# Ver logs del contenedor
docker-compose logs --tail=100 web

# Verificar health check
docker inspect certificados_web_dev | grep -A 20 Health

# Ejecutar comando manualmente para debug
docker-compose run --rm web bash
```

### Problema: Migraciones no se aplican

```bash
# Ejecutar migraciones manualmente
docker-compose exec web python manage.py migrate

# Ver estado de migraciones
docker-compose exec web python manage.py showmigrations

# Crear migraciones
docker-compose exec web python manage.py makemigrations
```

## Testing de Configuración

Se incluyen scripts de testing para verificar la configuración:

### Linux/Mac

```bash
chmod +x test-docker-compose.sh
./test-docker-compose.sh
```

### Windows

```cmd
test-docker-compose.bat
```

Los tests verifican:

1. Existencia de archivos de configuración
2. Sintaxis válida de Docker Compose
3. Servicios definidos correctamente
4. Volúmenes persistentes configurados
5. Health checks implementados
6. Redes personalizadas
7. Dependencias entre servicios

## Mejores Prácticas

1. **Desarrollo**: Usar `docker-compose.yml` con hot-reload
2. **Producción**: Usar `docker-compose.prod.yml` con optimizaciones
3. **Backups**: Configurar backups automáticos en producción
4. **Logs**: Rotar logs regularmente para evitar llenar disco
5. **Seguridad**: Nunca commitear `.env.production` con credenciales reales
6. **Monitoreo**: Usar health checks para detectar problemas temprano
7. **Actualizaciones**: Probar en desarrollo antes de aplicar en producción

## Referencias

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Redis Docker Hub](https://hub.docker.com/_/redis)
- [Nginx Docker Hub](https://hub.docker.com/_/nginx)
