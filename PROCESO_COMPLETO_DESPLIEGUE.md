# Proceso Completo de Despliegue - Corrección de Archivos Estáticos

## Problemas Identificados

1. ✅ **Permisos de entrypoint.sh** - El archivo no tenía permisos de ejecución (+x)
2. ✅ **Configuración nginx HTTPS** - Nginx estaba configurado para HTTPS pero no hay certificados SSL
3. ✅ **Archivos estáticos 404** - Los archivos CSS/JS no se estaban sirviendo correctamente

## Soluciones Implementadas

### 1. Permisos de entrypoint.sh
- Agregado `chmod +x entrypoint.sh` en el proceso de Git
- El archivo ahora se sube a GitHub con permisos de ejecución

### 2. Configuración Nginx HTTP
- Creado `nginx.prod.http-only.conf` - Configuración simplificada para HTTP
- Sin redirecciones a HTTPS
- Sirve archivos estáticos correctamente desde `/app/staticfiles/`
- Listo para usar con reverse proxy externo después

### 3. Archivos Estáticos
- Comando `collectstatic` se ejecuta en el contenedor
- Nginx sirve archivos desde `/app/staticfiles/`
- WhiteNoise maneja compresión y cache

## Archivos Creados

### Para Windows (Ejecutar AHORA)
- `SUBIR_A_GITHUB_AHORA.bat` - Sube todos los cambios a GitHub

### Para Ubuntu (Ejecutar DESPUÉS)
- `ACTUALIZAR_EN_UBUNTU.txt` - Comandos completos para actualizar desde GitHub
- `DESPLIEGUE_HTTP_FINAL.txt` - Comandos resumidos para despliegue

### Documentación
- `AGREGAR_REVERSE_PROXY_DESPUES.md` - Guía para agregar HTTPS con reverse proxy
- `nginx.prod.http-only.conf` - Configuración de nginx para HTTP

## Proceso de Despliegue

### FASE 1: En Windows (TU MÁQUINA)

```batch
# Ejecutar este archivo:
SUBIR_A_GITHUB_AHORA.bat
```

Esto hará:
1. Dar permisos +x a entrypoint.sh
2. Agregar todos los cambios
3. Commit con mensaje descriptivo
4. Push a GitHub

### FASE 2: En Ubuntu (SERVIDOR)

```bash
# Copiar y pegar comandos de:
ACTUALIZAR_EN_UBUNTU.txt
```

Esto hará:
1. Actualizar código desde GitHub
2. Reconstruir imagen con entrypoint.sh correcto
3. Copiar configuración nginx HTTP
4. Recolectar archivos estáticos
5. Reiniciar servicios

### FASE 3: Verificación

Abrir en navegador:
- URL: http://161.132.47.92:7070/admin/
- Usuario: admin
- Contraseña: admin123

Deberías ver:
- ✅ Página de login del admin de Django
- ✅ Estilos CSS cargando correctamente
- ✅ Sin errores 404 en la consola del navegador

## Arquitectura Actual

```
Internet
    ↓
http://161.132.47.92:7070
    ↓
Nginx (contenedor) - Puerto 80 interno
    ↓
    ├─→ /static/ → /app/staticfiles/ (archivos estáticos)
    ├─→ /media/ → /app/media/ (archivos subidos)
    └─→ / → Django (web:8000) (aplicación)
```

## Próximos Pasos (Opcional - HTTPS)

Cuando quieras agregar HTTPS, tienes 3 opciones:

### Opción 1: Nginx Reverse Proxy (Recomendado para IP)
- Instalar nginx en el host
- Configurar proxy_pass a localhost:7070
- Usar certificado autofirmado

### Opción 2: Caddy (Recomendado para dominio)
- SSL automático con Let's Encrypt
- Configuración muy simple
- Renovación automática

### Opción 3: Traefik (Para múltiples servicios)
- Dashboard web
- SSL automático
- Perfecto si tienes varios servicios

Ver detalles en: `AGREGAR_REVERSE_PROXY_DESPUES.md`

## Ventajas de Este Enfoque

✅ **Separación de responsabilidades**
- Aplicación solo maneja HTTP
- Reverse proxy maneja SSL/HTTPS
- Fácil de mantener y escalar

✅ **Flexibilidad**
- Puedes cambiar de reverse proxy sin tocar la aplicación
- Puedes agregar/quitar HTTPS cuando quieras
- Fácil de probar localmente

✅ **Seguridad**
- Nginx interno solo escucha en red Docker
- Puerto 7070 expuesto para reverse proxy
- Puedes agregar firewall rules fácilmente

## Troubleshooting

### Si los archivos estáticos siguen sin cargar:

```bash
# 1. Verificar que existen
docker compose -f docker-compose.prod.yml --env-file .env.production exec web ls -la /app/staticfiles/admin/css/

# 2. Verificar configuración nginx
docker compose -f docker-compose.prod.yml --env-file .env.production exec nginx cat /etc/nginx/nginx.conf

# 3. Ver logs de nginx
docker compose -f docker-compose.prod.yml --env-file .env.production logs nginx

# 4. Probar acceso directo
curl -I http://161.132.47.92:7070/static/admin/css/base.css
```

### Si el contenedor web no inicia:

```bash
# Ver logs
docker compose -f docker-compose.prod.yml --env-file .env.production logs web

# Verificar permisos de entrypoint.sh
docker compose -f docker-compose.prod.yml --env-file .env.production exec web ls -la /app/entrypoint.sh

# Reconstruir sin cache
docker compose -f docker-compose.prod.yml --env-file .env.production build --no-cache web
```

## Resumen de Comandos Rápidos

### Windows
```batch
SUBIR_A_GITHUB_AHORA.bat
```

### Ubuntu
```bash
cd ~/drtc_certificados
git pull origin main
chmod +x entrypoint.sh
docker compose -f docker-compose.prod.yml --env-file .env.production down
docker compose -f docker-compose.prod.yml --env-file .env.production build --no-cache web
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
docker cp nginx.prod.http-only.conf certificados-drtc-nginx-1:/etc/nginx/nginx.conf
docker compose -f docker-compose.prod.yml --env-file .env.production exec nginx nginx -s reload
docker compose -f docker-compose.prod.yml --env-file .env.production exec web python manage.py collectstatic --noinput --clear
```

## Contacto y Soporte

Si encuentras algún problema:
1. Revisa los logs: `docker compose logs`
2. Verifica el estado: `docker compose ps`
3. Consulta este documento
4. Revisa `AGREGAR_REVERSE_PROXY_DESPUES.md` para HTTPS

---

**Fecha de creación:** 2025-01-12  
**Versión:** 1.0  
**Estado:** Listo para despliegue
