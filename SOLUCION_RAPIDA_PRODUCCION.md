# 🚨 Solución Rápida al Error de Producción

## Error Actual
```
Error response from daemon: failed to create task for container: 
failed to create shim task: OCI runtime create failed: 
runc create failed: unable to start container process: 
error during container init: exec: "/app/entrypoint.sh": 
permission denied: unknown
```

## ✅ Solución en 3 Pasos

### Paso 1: Detener Contenedores
```cmd
docker compose -f docker-compose.prod.yml down
```

### Paso 2: Reconstruir con Permisos Correctos
```cmd
docker compose -f docker-compose.prod.yml build --no-cache web
```

### Paso 3: Iniciar de Nuevo
```cmd
docker compose -f docker-compose.prod.yml up -d
```

## 🎯 Solución Completa Automatizada

Ejecuta el script de despliegue:

```cmd
deploy-production.bat
```

Este script hace todo automáticamente:
- ✅ Limpia contenedores anteriores
- ✅ Configura permisos correctos
- ✅ Construye imágenes
- ✅ Inicia servicios
- ✅ Verifica que todo funcione

## 📋 Verificación

Después de ejecutar, verifica que todo esté corriendo:

```cmd
REM Ver estado de contenedores
docker compose -f docker-compose.prod.yml ps

REM Ver logs
docker compose -f docker-compose.prod.yml logs -f

REM Verificar health check
curl http://localhost/health/
```

## 🌐 Acceder a la Aplicación

Una vez que los servicios estén corriendo:

- **Página principal:** http://localhost/
- **Admin:** http://localhost/admin/
- **Health check:** http://localhost/health/
- **API:** http://localhost/api/

## 🔧 Si Aún Tienes Problemas

### Ver Logs Detallados
```cmd
docker compose -f docker-compose.prod.yml logs web --tail=100
```

### Verificar Permisos del Entrypoint
```cmd
docker compose -f docker-compose.prod.yml run --rm web ls -la /app/entrypoint.sh
```

Deberías ver algo como:
```
-rwxr-xr-x 1 app app 789 Nov 10 12:00 /app/entrypoint.sh
```

El `-rwxr-xr-x` indica que tiene permisos de ejecución (x).

### Reconstruir Completamente
```cmd
REM Limpiar todo
docker compose -f docker-compose.prod.yml down -v
docker system prune -f

REM Reconstruir desde cero
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

## 📞 Comandos Útiles

```cmd
REM Ver estado
docker compose -f docker-compose.prod.yml ps

REM Ver logs en tiempo real
docker compose -f docker-compose.prod.yml logs -f

REM Reiniciar un servicio
docker compose -f docker-compose.prod.yml restart web

REM Detener todo
docker compose -f docker-compose.prod.yml stop

REM Eliminar todo
docker compose -f docker-compose.prod.yml down -v
```

## ✨ Cambios Realizados

He actualizado el `Dockerfile` para incluir:

```dockerfile
# Copiar script de entrada primero (como root para dar permisos)
COPY entrypoint.sh /app/entrypoint.sh

# Dar permisos de ejecución al entrypoint
RUN chmod +x /app/entrypoint.sh && chown app:app /app/entrypoint.sh
```

Esto asegura que el `entrypoint.sh` siempre tenga permisos de ejecución, independientemente del sistema operativo donde se construya la imagen.

## 🎉 ¡Listo!

Ahora puedes desplegar a producción sin problemas de permisos.

**Ejecuta:**
```cmd
deploy-production.bat
```

Y sigue las instrucciones en pantalla.
