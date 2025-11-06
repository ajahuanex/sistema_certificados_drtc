# 🔧 COMANDOS DE TROUBLESHOOTING - PRODUCCIÓN

## 🚨 **COMANDOS DE EMERGENCIA**

### Reinicio Completo del Sistema
```bash
# Detener todo
docker-compose -f docker-compose.prod.yml down

# Limpiar redes y volúmenes
docker network prune -f
docker volume prune -f

# Reconstruir y reiniciar
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### Verificación Rápida de Estado
```bash
# Estado de contenedores
docker-compose -f docker-compose.prod.yml ps

# Logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f web

# Health checks
docker-compose -f docker-compose.prod.yml exec web curl -f http://localhost:8000/health/
```

## 🔍 **DIAGNÓSTICO DE PROBLEMAS**

### 1. Error de Settings Module
```bash
# Verificar variables de entorno
docker-compose -f docker-compose.prod.yml exec web env | grep DJANGO

# Verificar archivos de settings
docker-compose -f docker-compose.prod.yml exec web ls -la config/settings/

# Probar importación manual
docker-compose -f docker-compose.prod.yml exec web python -c "import config.settings.base; print('OK')"
```

### 2. Problemas de Base de Datos
```bash
# Verificar conexión a PostgreSQL
docker-compose -f docker-compose.prod.yml exec db pg_isready -U certificados_user

# Conectar a la base de datos
docker-compose -f docker-compose.prod.yml exec db psql -U certificados_user -d certificados_prod

# Verificar migraciones
docker-compose -f docker-compose.prod.yml exec web python manage.py showmigrations
```

### 3. Problemas de Redis
```bash
# Verificar Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping

# Ver información de Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli info
```

### 4. Problemas de Nginx
```bash
# Verificar configuración de Nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Recargar configuración
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

# Ver logs de Nginx
docker-compose -f docker-compose.prod.yml logs nginx
```

## 🛠️ **COMANDOS DE MANTENIMIENTO**

### Backup de Base de Datos
```bash
# Crear backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U certificados_user certificados_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar backup
docker-compose -f docker-compose.prod.yml exec -T db psql -U certificados_user certificados_prod < backup_file.sql
```

### Limpieza de Logs
```bash
# Limpiar logs de Docker
docker system prune -f

# Ver tamaño de logs
docker-compose -f docker-compose.prod.yml exec web du -sh /app/logs/
```

### Actualización de Código
```bash
# Reconstruir solo la aplicación web
docker-compose -f docker-compose.prod.yml build --no-cache web
docker-compose -f docker-compose.prod.yml up -d web

# Ejecutar migraciones
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Recopilar archivos estáticos
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

## 📊 **MONITOREO**

### Verificar Recursos
```bash
# Uso de CPU y memoria
docker stats

# Espacio en disco
df -h

# Logs de sistema
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### Health Checks
```bash
# Verificar todos los servicios
curl -f http://localhost/health/
curl -f http://localhost/admin/

# Verificar base de datos desde Django
docker-compose -f docker-compose.prod.yml exec web python manage.py check --database default
```

## 🚨 **SOLUCIÓN DE PROBLEMAS COMUNES**

### Error: "ModuleNotFoundError: config.settings.minimal"
```bash
# Solución: Cambiar a settings.base
docker-compose -f docker-compose.prod.yml down
# Editar docker-compose.prod.yml: DJANGO_SETTINGS_MODULE=config.settings.base
docker-compose -f docker-compose.prod.yml up -d
```

### Error: "Permission denied" en logs
```bash
# Solución: Usar logging solo a consola
# Ya corregido en config/settings/base.py
docker-compose -f docker-compose.prod.yml restart web
```

### Error: "Database connection failed"
```bash
# Verificar variables de entorno
cat .env.production | grep DB_

# Verificar que PostgreSQL esté corriendo
docker-compose -f docker-compose.prod.yml ps db

# Reiniciar base de datos
docker-compose -f docker-compose.prod.yml restart db
```

### Error: "Network overlap"
```bash
# Limpiar redes Docker
docker network prune -f
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

## 📞 **CONTACTO DE EMERGENCIA**

Si los problemas persisten:
1. Revisar logs completos: `docker-compose -f docker-compose.prod.yml logs`
2. Verificar configuración: `cat .env.production`
3. Reinicio completo del sistema
4. Contactar al equipo de desarrollo con logs específicos

---

**Última actualización**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")