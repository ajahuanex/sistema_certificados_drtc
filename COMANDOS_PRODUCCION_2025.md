# 🚀 Comandos de Producción - Docker Compose v2 (2025)

## ⚡ Comandos Rápidos

### Despliegue Completo
```cmd
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

### Ver Estado
```cmd
docker compose -f docker-compose.prod.yml ps
```

### Ver Logs
```cmd
docker compose -f docker-compose.prod.yml logs -f
```

---

## 📦 Gestión de Servicios

### Iniciar Servicios
```cmd
docker compose -f docker-compose.prod.yml up -d
```

### Detener Servicios
```cmd
docker compose -f docker-compose.prod.yml stop
```

### Reiniciar Servicios
```cmd
docker compose -f docker-compose.prod.yml restart
```

### Reiniciar un Servicio Específico
```cmd
docker compose -f docker-compose.prod.yml restart web
docker compose -f docker-compose.prod.yml restart db
docker compose -f docker-compose.prod.yml restart redis
docker compose -f docker-compose.prod.yml restart nginx
```

### Detener y Eliminar
```cmd
docker compose -f docker-compose.prod.yml down
```

### Detener y Eliminar con Volúmenes
```cmd
docker compose -f docker-compose.prod.yml down -v
```

---

## 🔨 Construcción

### Construir Todas las Imágenes
```cmd
docker compose -f docker-compose.prod.yml build
```

### Construir sin Caché
```cmd
docker compose -f docker-compose.prod.yml build --no-cache
```

### Construir un Servicio Específico
```cmd
docker compose -f docker-compose.prod.yml build web
```

---

## 📊 Monitoreo

### Ver Logs en Tiempo Real
```cmd
docker compose -f docker-compose.prod.yml logs -f
```

### Ver Logs de un Servicio
```cmd
docker compose -f docker-compose.prod.yml logs web -f
docker compose -f docker-compose.prod.yml logs db -f
docker compose -f docker-compose.prod.yml logs redis -f
docker compose -f docker-compose.prod.yml logs nginx -f
```

### Ver Últimas N Líneas
```cmd
docker compose -f docker-compose.prod.yml logs --tail=50
docker compose -f docker-compose.prod.yml logs web --tail=100
```

### Ver Estado de Servicios
```cmd
docker compose -f docker-compose.prod.yml ps
```

### Ver Uso de Recursos
```cmd
docker stats
```

---

## 🐍 Comandos Django

### Ejecutar Migraciones
```cmd
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### Crear Superusuario
```cmd
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### Recopilar Archivos Estáticos
```cmd
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### Shell de Django
```cmd
docker compose -f docker-compose.prod.yml exec web python manage.py shell
```

### Ejecutar Comando Personalizado
```cmd
docker compose -f docker-compose.prod.yml exec web python manage.py tu_comando
```

### Ejecutar Tests
```cmd
docker compose -f docker-compose.prod.yml exec web python manage.py test
```

---

## 🗄️ Base de Datos

### Conectar a PostgreSQL
```cmd
docker compose -f docker-compose.prod.yml exec db psql -U certificados_user -d certificados_prod
```

### Backup de Base de Datos
```cmd
docker compose -f docker-compose.prod.yml exec db pg_dump -U certificados_user certificados_prod > backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.sql
```

### Restore de Base de Datos
```cmd
docker compose -f docker-compose.prod.yml exec -T db psql -U certificados_user certificados_prod < backup.sql
```

### Ver Tablas
```cmd
docker compose -f docker-compose.prod.yml exec db psql -U certificados_user -d certificados_prod -c "\dt"
```

### Ver Tamaño de Base de Datos
```cmd
docker compose -f docker-compose.prod.yml exec db psql -U certificados_user -d certificados_prod -c "SELECT pg_size_pretty(pg_database_size('certificados_prod'));"
```

---

## 🔴 Redis

### Conectar a Redis
```cmd
docker compose -f docker-compose.prod.yml exec redis redis-cli
```

### Ping a Redis
```cmd
docker compose -f docker-compose.prod.yml exec redis redis-cli PING
```

### Ver Todas las Claves
```cmd
docker compose -f docker-compose.prod.yml exec redis redis-cli KEYS "*"
```

### Limpiar Cache
```cmd
docker compose -f docker-compose.prod.yml exec redis redis-cli FLUSHALL
```

---

## 📁 Archivos y Volúmenes

### Copiar Archivos desde Contenedor
```cmd
docker cp certificados_web_prod:/app/media ./media_backup
```

### Copiar Archivos a Contenedor
```cmd
docker cp ./media_backup certificados_web_prod:/app/media
```

### Ver Volúmenes
```cmd
docker volume ls
```

### Inspeccionar Volumen
```cmd
docker volume inspect sistema_certificados_drtc_postgres_data
docker volume inspect sistema_certificados_drtc_media_files
```

### Limpiar Volúmenes No Usados
```cmd
docker volume prune -f
```

---

## 🔍 Inspección y Debug

### Ver Procesos en un Contenedor
```cmd
docker compose -f docker-compose.prod.yml exec web ps aux
```

### Ver Variables de Entorno
```cmd
docker compose -f docker-compose.prod.yml exec web env
```

### Ver Espacio en Disco
```cmd
docker compose -f docker-compose.prod.yml exec web df -h
```

### Ejecutar Bash en Contenedor
```cmd
docker compose -f docker-compose.prod.yml exec web bash
```

### Ver Configuración de Docker Compose
```cmd
docker compose -f docker-compose.prod.yml config
```

### Inspeccionar Contenedor
```cmd
docker inspect certificados_web_prod
```

---

## 🧹 Limpieza

### Limpiar Contenedores Detenidos
```cmd
docker container prune -f
```

### Limpiar Imágenes No Usadas
```cmd
docker image prune -a -f
```

### Limpiar Todo el Sistema
```cmd
docker system prune -a -f --volumes
```

### Limpiar Solo Volúmenes
```cmd
docker volume prune -f
```

---

## 🔄 Actualización

### Actualizar Código y Reiniciar
```cmd
git pull
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d
```

### Actualizar con Migraciones
```cmd
git pull
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker compose -f docker-compose.prod.yml restart web
```

---

## 🚨 Troubleshooting

### Ver Logs Detallados
```cmd
docker compose -f docker-compose.prod.yml logs --tail=200
```

### Verificar Health Checks
```cmd
curl http://localhost/health/
```

### Reiniciar Todo
```cmd
docker compose -f docker-compose.prod.yml restart
```

### Reconstruir Completamente
```cmd
docker compose -f docker-compose.prod.yml down -v
docker system prune -f
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

### Ver Errores de un Servicio
```cmd
docker compose -f docker-compose.prod.yml logs web --tail=100 | findstr ERROR
```

---

## 📈 Monitoreo Continuo

### Script de Monitoreo (crear monitor.bat)
```cmd
@echo off
:loop
cls
echo ========================================
echo Estado de Servicios
echo ========================================
docker compose -f docker-compose.prod.yml ps
echo.
echo ========================================
echo Health Check
echo ========================================
curl -s http://localhost/health/
echo.
echo.
echo Actualizando en 30 segundos...
timeout /t 30 /nobreak >nul
goto loop
```

---

## 💡 Diferencias con Docker Compose v1

### Antiguo (v1)
```cmd
docker-compose -f docker-compose.prod.yml up -d
```

### Nuevo (v2)
```cmd
docker compose -f docker-compose.prod.yml up -d
```

**Cambios principales:**
- ❌ `docker-compose` (con guión) - Comando separado
- ✅ `docker compose` (sin guión) - Subcomando de Docker CLI

---

## 🎯 Comandos Más Usados

```cmd
REM 1. Ver estado
docker compose -f docker-compose.prod.yml ps

REM 2. Ver logs
docker compose -f docker-compose.prod.yml logs -f

REM 3. Reiniciar
docker compose -f docker-compose.prod.yml restart

REM 4. Ejecutar migraciones
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

REM 5. Backup de BD
docker compose -f docker-compose.prod.yml exec db pg_dump -U certificados_user certificados_prod > backup.sql
```

---

## 📞 Ayuda Rápida

Si tienes problemas:

1. **Ver logs:**
   ```cmd
   docker compose -f docker-compose.prod.yml logs --tail=100
   ```

2. **Verificar estado:**
   ```cmd
   docker compose -f docker-compose.prod.yml ps
   ```

3. **Reiniciar:**
   ```cmd
   docker compose -f docker-compose.prod.yml restart
   ```

4. **Reconstruir:**
   ```cmd
   docker compose -f docker-compose.prod.yml down
   docker compose -f docker-compose.prod.yml build --no-cache
   docker compose -f docker-compose.prod.yml up -d
   ```

---

**Última actualización:** 2025-11-10  
**Versión:** Docker Compose v2  
**Sintaxis:** `docker compose` (sin guión)
