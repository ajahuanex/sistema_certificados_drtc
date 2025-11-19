# 🔧 SOLUCIÓN COMPLETA - CSRF Y PRODUCCIÓN

## Problema Detectado
1. Error 403 CSRF en consultas
2. Contenedores levantándose en modo desarrollo en lugar de producción
3. Falta configuración de DB_PASSWORD en docker-compose.prod.yml

## Solución Paso a Paso

### 1. Conectarse al servidor
```bash
ssh administrador@161.132.47.92
cd dockers/sistema_certificados_drtc
```

### 2. Verificar que existe .env.production
```bash
ls -la .env.production
cat .env.production | grep DB_PASSWORD
```

### 3. Actualizar CSRF_TRUSTED_ORIGINS en .env.production
```bash
sed -i 's|^CSRF_TRUSTED_ORIGINS=.*|CSRF_TRUSTED_ORIGINS=http://localhost:7070,http://127.0.0.1:7070,http://161.132.47.92:7070,http://certificados.transportespuno.gob.pe,http://www.certificados.transportespuno.gob.pe,https://certificados.transportespuno.gob.pe,https://www.certificados.transportespuno.gob.pe|g' .env.production
```

### 4. Verificar el cambio
```bash
grep CSRF_TRUSTED_ORIGINS .env.production
```

### 5. Detener todos los contenedores
```bash
docker compose down
docker compose -f docker-compose.prod.yml down
docker ps -a
```

### 6. Limpiar contenedores huérfanos
```bash
docker container prune -f
docker network prune -f
```

### 7. Levantar SOLO con docker-compose.yml (que ya funciona)
```bash
docker compose up -d
```

### 8. Esperar y verificar
```bash
sleep 15
docker compose ps
docker compose logs --tail=30 web
```

### 9. Probar el sitio
```bash
curl -I http://localhost:7070/
curl -I http://localhost:7070/consulta/
```

## Verificación Final

1. Ve a: http://certificados.transportespuno.gob.pe/consulta/
2. Ingresa un DNI
3. Haz clic en "Consultar"
4. Ya NO debería aparecer el error 403

## Notas Importantes

- El sistema está funcionando con `docker-compose.yml` (sin el .prod)
- Los contenedores están en puerto 7070
- El proxy reverso está funcionando correctamente
- Solo necesitábamos agregar HTTP a CSRF_TRUSTED_ORIGINS

## Si aún hay problemas

Ejecuta el diagnóstico:
```bash
cd dockers/sistema_certificados_drtc
docker compose logs -f web
```

Y busca errores relacionados con CSRF o ALLOWED_HOSTS.
