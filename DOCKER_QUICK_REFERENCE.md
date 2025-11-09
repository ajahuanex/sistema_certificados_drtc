# Docker Compose - Referencia Rápida

## Comandos Esenciales

### Desarrollo

```bash
# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down

# Reiniciar
docker-compose restart

# Reconstruir
docker-compose up -d --build
```

### Producción

```bash
# Iniciar
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Detener
docker-compose -f docker-compose.prod.yml down

# Actualizar
docker-compose -f docker-compose.prod.yml up -d --build
```

## Servicios

### Desarrollo
- **Web**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Adminer**: http://localhost:8080 (con --profile admin)

### Producción
- **Web (Nginx)**: http://localhost:8181 (HTTP), https://localhost:8443 (HTTPS)
- **Monitoreo**: http://localhost:9100 (con --profile monitoring)

## Django Commands

```bash
# Migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Archivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Tests
docker-compose exec web python manage.py test

# Shell
docker-compose exec web python manage.py shell
```

## Base de Datos

```bash
# Acceder a PostgreSQL
docker-compose exec db psql -U certificados_user -d certificados_dev

# Backup
docker-compose exec db pg_dump -U certificados_user certificados_dev > backup.sql

# Restaurar
docker-compose exec -T db psql -U certificados_user -d certificados_dev < backup.sql
```

## Troubleshooting

```bash
# Ver estado
docker-compose ps

# Ver logs de un servicio
docker-compose logs -f web

# Reiniciar un servicio
docker-compose restart web

# Ejecutar comando en contenedor
docker-compose exec web bash

# Limpiar todo
docker-compose down -v
```

## Health Checks

```bash
# Verificar estado de servicios
docker-compose ps

# Ver health check de un servicio
docker inspect certificados_web_dev | grep -A 10 Health
```

## Testing

```bash
# Windows
test-docker-compose.bat

# Linux/Mac
./test-docker-compose.sh
```
