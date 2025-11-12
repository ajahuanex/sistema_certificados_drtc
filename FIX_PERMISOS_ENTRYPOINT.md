# Solución Error de Permisos - entrypoint.sh

## Problema
El contenedor web no puede ejecutar el `entrypoint.sh` porque no tiene permisos de ejecución.

## Solución - Ejecuta estos comandos en Ubuntu

### Paso 1: Dar permisos de ejecución al archivo
```bash
chmod +x entrypoint.sh
```

### Paso 2: Verificar que los permisos se aplicaron
```bash
ls -la entrypoint.sh
```
Deberías ver algo como: `-rwxr-xr-x` (la 'x' indica que es ejecutable)

### Paso 3: Reconstruir la imagen sin caché
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production build --no-cache web
```

### Paso 4: Levantar el servicio web
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d web
```

### Paso 5: Esperar 30 segundos y verificar logs
```bash
sleep 30
docker compose -f docker-compose.prod.yml --env-file .env.production logs web
```

### Paso 6: Probar el acceso
Abre en tu navegador: **http://161.132.47.92:7070/admin/**

---

## Plan B: Si sigue fallando

Si después de aplicar los permisos sigue sin funcionar, usa la imagen anterior:

```bash
# Detener el servicio
docker compose -f docker-compose.prod.yml --env-file .env.production stop web

# Eliminar el contenedor
docker compose -f docker-compose.prod.yml --env-file .env.production rm -f web

# Levantar sin reconstruir (usa imagen anterior)
docker compose -f docker-compose.prod.yml --env-file .env.production up -d web --no-build
```

---

## Verificación Final

Verifica que todo esté funcionando:

```bash
# Ver estado de los contenedores
docker compose -f docker-compose.prod.yml --env-file .env.production ps

# Ver logs en tiempo real
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f web
```

---

## Notas
- El problema es que el archivo `entrypoint.sh` no tenía permisos de ejecución (+x)
- Al reconstruir con `--no-cache` forzamos que Docker copie el archivo con los nuevos permisos
- Si usas Git, asegúrate de que los permisos se mantengan al hacer commit
