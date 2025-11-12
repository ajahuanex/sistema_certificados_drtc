# 🚀 DESPLEGAR A PRODUCCIÓN - Comandos Actualizados 2025

## ⚡ Solución Inmediata (3 comandos)

Ejecuta estos comandos en tu terminal:

```cmd
docker compose -f docker-compose.prod.yml down
```

```cmd
docker compose -f docker-compose.prod.yml build --no-cache web
```

```cmd
docker compose -f docker-compose.prod.yml up -d
```

---

## 🎯 Opción Automatizada (Recomendada)

Ejecuta el script de despliegue:

```cmd
deploy-production.bat
```

Este script ya está actualizado con la sintaxis correcta de Docker Compose v2.

---

## ✅ Verificar Estado

```cmd
docker compose -f docker-compose.prod.yml ps
```

Deberías ver:
```
NAME                          STATUS
certificados_db_prod          Up (healthy)
certificados_redis_prod       Up (healthy)
certificados_web_prod         Up
certificados_nginx_prod       Up
```

---

## 🌐 Acceder a la Aplicación

Una vez que todos los servicios estén "Up":

- **Página principal:** http://localhost/
- **Admin:** http://localhost/admin/
- **Health check:** http://localhost/health/
- **API:** http://localhost/api/

---

## 📊 Ver Logs

```cmd
REM Ver logs de todos los servicios
docker compose -f docker-compose.prod.yml logs -f

REM Ver logs solo del servicio web
docker compose -f docker-compose.prod.yml logs web -f

REM Ver últimas 50 líneas
docker compose -f docker-compose.prod.yml logs --tail=50
```

Presiona `Ctrl+C` para salir de los logs.

---

## 🔄 Comandos Útiles

### Reiniciar Servicios
```cmd
docker compose -f docker-compose.prod.yml restart
```

### Reiniciar Solo un Servicio
```cmd
docker compose -f docker-compose.prod.yml restart web
```

### Detener Servicios
```cmd
docker compose -f docker-compose.prod.yml stop
```

### Iniciar Servicios Detenidos
```cmd
docker compose -f docker-compose.prod.yml start
```

### Detener y Eliminar Todo
```cmd
docker compose -f docker-compose.prod.yml down -v
```

---

## 🔧 Ejecutar Comandos Django

### Migraciones
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

---

## 💾 Backup

### Backup de Base de Datos
```cmd
docker compose -f docker-compose.prod.yml exec db pg_dump -U certificados_user certificados_prod > backup.sql
```

### Restore de Base de Datos
```cmd
docker compose -f docker-compose.prod.yml exec -T db psql -U certificados_user certificados_prod < backup.sql
```

---

## 🔍 Troubleshooting

### Ver Logs Detallados
```cmd
docker compose -f docker-compose.prod.yml logs web --tail=100
```

### Verificar Conexión a PostgreSQL
```cmd
docker compose -f docker-compose.prod.yml exec db psql -U certificados_user -d certificados_prod
```

### Verificar Conexión a Redis
```cmd
docker compose -f docker-compose.prod.yml exec redis redis-cli PING
```

### Reconstruir Completamente
```cmd
docker compose -f docker-compose.prod.yml down -v
docker system prune -f
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

---

## 📈 Monitoreo

### Ver Uso de Recursos
```cmd
docker stats
```

### Ver Procesos en un Contenedor
```cmd
docker compose -f docker-compose.prod.yml exec web ps aux
```

### Inspeccionar Contenedor
```cmd
docker compose -f docker-compose.prod.yml exec web df -h
```

---

## 🎯 Checklist Rápido

- [ ] Docker Desktop corriendo
- [ ] Archivo `.env.production` configurado
- [ ] Ejecutar `deploy-production.bat`
- [ ] Verificar que todos los servicios están "Up"
- [ ] Abrir http://localhost/ en navegador
- [ ] Iniciar sesión en http://localhost/admin/
- [ ] Verificar que todo funciona correctamente

---

## 💡 Notas Importantes

### Diferencia entre docker-compose y docker compose

- ❌ **Antiguo:** `docker-compose` (con guión)
- ✅ **Nuevo:** `docker compose` (sin guión)

Docker Compose v2 está integrado en Docker Desktop y usa `docker compose` como subcomando.

### Si tienes problemas con el comando

Si `docker compose` no funciona, verifica tu versión de Docker:

```cmd
docker --version
docker compose version
```

Deberías tener Docker Desktop 3.4 o superior.

---

## 🚨 Solución al Error de Permisos

El error que tenías:
```
exec: "/app/entrypoint.sh": permission denied
```

Ya está solucionado en el `Dockerfile` actualizado. Solo necesitas reconstruir la imagen:

```cmd
docker compose -f docker-compose.prod.yml build --no-cache web
docker compose -f docker-compose.prod.yml up -d
```

---

## 📞 Ayuda Adicional

Si necesitas más ayuda, consulta:

- `DESPLIEGUE_PRODUCCION_COMPLETO.md` - Guía completa
- `CHECKLIST_DESPLIEGUE.md` - Checklist detallado
- `COMANDOS_RAPIDOS_PRODUCCION.md` - Referencia de comandos

---

## 🎉 ¡Listo!

Tu aplicación debería estar corriendo en:
- http://localhost/

**Credenciales de admin:**
- Usuario: Configurado en `.env.production` (`DJANGO_SUPERUSER_USERNAME`)
- Password: Configurado en `.env.production` (`DJANGO_SUPERUSER_PASSWORD`)

---

**Última actualización:** 2025-11-10  
**Sintaxis:** Docker Compose v2 (sin guión)
