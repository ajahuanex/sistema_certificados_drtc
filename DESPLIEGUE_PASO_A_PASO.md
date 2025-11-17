# 🚀 Despliegue Paso a Paso - Sistema Certificados DRTC

## 📋 Resumen del Problema y Solución

### Problemas Encontrados
1. ❌ Contenedor web no iniciaba - `entrypoint.sh` sin permisos de ejecución
2. ❌ Archivos estáticos 404 - Nginx configurado para HTTPS sin certificados
3. ❌ Warnings de CORS - Configuración de seguridad incorrecta

### Soluciones Aplicadas
1. ✅ Permisos +x a `entrypoint.sh`
2. ✅ Nueva configuración nginx HTTP: `nginx.prod.http-only.conf`
3. ✅ Documentación para agregar HTTPS después con reverse proxy

---

## 🔄 FASE 1: Subir Cambios a GitHub (Windows)

### Opción A: Usar el archivo BAT (Recomendado)
```batch
SUBIR_A_GITHUB_AHORA.bat
```

### Opción B: Comandos manuales
```bash
git update-index --chmod=+x entrypoint.sh
git add .
git commit -m "Fix: Nginx HTTP config y permisos entrypoint - Archivos estaticos corregidos"
git push origin main
```

### ✅ Verificación
Después del push, verifica en GitHub que los archivos se subieron:
- `entrypoint.sh` (con permisos +x)
- `nginx.prod.http-only.conf`
- `ACTUALIZAR_EN_UBUNTU.txt`
- `PROCESO_COMPLETO_DESPLIEGUE.md`

---

## 🐧 FASE 2: Actualizar en Ubuntu (Servidor)

### Paso 1: Conectarse al servidor
```bash
ssh usuario@161.132.47.92
```

### Paso 2: Ir al directorio del proyecto
```bash
cd ~/drtc_certificados
```

### Paso 3: Hacer backup del .env (precaución)
```bash
cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)
```

### Paso 4: Detener contenedores
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production down
```

### Paso 5: Actualizar código desde GitHub
```bash
git pull origin main
```

### Paso 6: Verificar y dar permisos a entrypoint.sh
```bash
ls -la entrypoint.sh
chmod +x entrypoint.sh
ls -la entrypoint.sh
```
Deberías ver: `-rwxr-xr-x` (la 'x' indica ejecutable)

### Paso 7: Reconstruir imagen web
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production build --no-cache web
```
⏱️ Esto tomará 2-3 minutos

### Paso 8: Levantar todos los servicios
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
```

### Paso 9: Esperar a que inicien
```bash
sleep 30
```

### Paso 10: Ver estado de contenedores
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production ps
```
Todos deben estar "Up" (running)

### Paso 11: Identificar nombre del contenedor nginx
```bash
docker ps | grep nginx
```
Anota el nombre, probablemente: `certificados-drtc-nginx-1`

### Paso 12: Copiar configuración HTTP a nginx
```bash
# Reemplaza el nombre si es diferente
docker cp nginx.prod.http-only.conf certificados-drtc-nginx-1:/etc/nginx/nginx.conf
```

### Paso 13: Verificar configuración de nginx
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production exec nginx nginx -t
```
Debe decir: `syntax is ok` y `test is successful`

### Paso 14: Recolectar archivos estáticos
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production exec web python manage.py collectstatic --noinput --clear
```
Verás mensajes de archivos copiados

### Paso 15: Recargar nginx
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production exec nginx nginx -s reload
```

### Paso 16: Ver logs para verificar
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production logs --tail=50 web
docker compose -f docker-compose.prod.yml --env-file .env.production logs --tail=50 nginx
```

---

## ✅ FASE 3: Verificación

### 1. Verificar archivos estáticos en el contenedor
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production exec web ls -la /app/staticfiles/admin/css/
```
Deberías ver archivos CSS como `base.css`, `dashboard.css`, etc.

### 2. Probar acceso a archivo estático
```bash
curl -I http://161.132.47.92:7070/static/admin/css/base.css
```
Debe responder: `HTTP/1.1 200 OK`

### 3. Verificar estado de todos los servicios
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production ps
```
Todos deben estar "Up" y "healthy"

### 4. Abrir en navegador
**URL:** http://161.132.47.92:7070/admin/

**Credenciales:**
- Usuario: `admin`
- Contraseña: `admin123`

### ✅ Checklist de Verificación
- [ ] Página de login carga correctamente
- [ ] Estilos CSS se aplican (colores, fuentes, layout)
- [ ] No hay errores 404 en la consola del navegador
- [ ] Puedes hacer login
- [ ] El dashboard del admin se ve correctamente

---

## 🔧 Troubleshooting

### Problema: Contenedor web no inicia

**Diagnóstico:**
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production logs web
```

**Soluciones:**
```bash
# Verificar permisos de entrypoint.sh
docker compose -f docker-compose.prod.yml --env-file .env.production exec web ls -la /app/entrypoint.sh

# Si no tiene permisos, reconstruir
chmod +x entrypoint.sh
docker compose -f docker-compose.prod.yml --env-file .env.production build --no-cache web
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
```

### Problema: Archivos estáticos 404

**Diagnóstico:**
```bash
# Ver si existen los archivos
docker compose -f docker-compose.prod.yml --env-file .env.production exec web ls -la /app/staticfiles/

# Ver configuración de nginx
docker compose -f docker-compose.prod.yml --env-file .env.production exec nginx cat /etc/nginx/nginx.conf | grep static
```

**Soluciones:**
```bash
# Recolectar archivos estáticos nuevamente
docker compose -f docker-compose.prod.yml --env-file .env.production exec web python manage.py collectstatic --noinput --clear

# Copiar configuración nginx nuevamente
docker cp nginx.prod.http-only.conf certificados-drtc-nginx-1:/etc/nginx/nginx.conf

# Recargar nginx
docker compose -f docker-compose.prod.yml --env-file .env.production exec nginx nginx -s reload
```

### Problema: No puedo conectarme al servidor

**Verificar:**
```bash
# Desde tu máquina Windows
ping 161.132.47.92

# Verificar que el puerto está abierto
telnet 161.132.47.92 7070
```

**Solución:**
```bash
# En Ubuntu, verificar firewall
sudo ufw status
sudo ufw allow 7070/tcp
```

### Problema: Base de datos no conecta

**Diagnóstico:**
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production logs db
docker compose -f docker-compose.prod.yml --env-file .env.production exec web python manage.py check --database default
```

**Solución:**
```bash
# Reiniciar servicio de base de datos
docker compose -f docker-compose.prod.yml --env-file .env.production restart db
sleep 10
docker compose -f docker-compose.prod.yml --env-file .env.production restart web
```

---

## 📊 Comandos Útiles

### Ver logs en tiempo real
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f
```

### Reiniciar un servicio específico
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production restart web
docker compose -f docker-compose.prod.yml --env-file .env.production restart nginx
docker compose -f docker-compose.prod.yml --env-file .env.production restart db
```

### Entrar a un contenedor
```bash
# Contenedor web
docker compose -f docker-compose.prod.yml --env-file .env.production exec web bash

# Contenedor nginx
docker compose -f docker-compose.prod.yml --env-file .env.production exec nginx sh

# Contenedor db
docker compose -f docker-compose.prod.yml --env-file .env.production exec db psql -U certificados_user -d certificados_prod
```

### Ver uso de recursos
```bash
docker stats
```

### Limpiar recursos Docker
```bash
# Limpiar contenedores detenidos
docker container prune -f

# Limpiar imágenes sin usar
docker image prune -a -f

# Limpiar volúmenes sin usar (¡CUIDADO! Esto borra datos)
docker volume prune -f
```

---

## 🔐 Próximos Pasos (Opcional)

### Agregar HTTPS con Reverse Proxy

Cuando estés listo para agregar HTTPS, consulta:
**`AGREGAR_REVERSE_PROXY_DESPUES.md`**

Opciones disponibles:
1. **Nginx Reverse Proxy** - Para IP sin dominio
2. **Caddy** - Para dominio con SSL automático
3. **Traefik** - Para múltiples servicios

---

## 📝 Notas Importantes

1. **Backup Regular**: Haz backup de la base de datos regularmente
   ```bash
   docker compose -f docker-compose.prod.yml --env-file .env.production exec db pg_dump -U certificados_user certificados_prod > backup_$(date +%Y%m%d).sql
   ```

2. **Monitoreo**: Revisa los logs periódicamente
   ```bash
   docker compose -f docker-compose.prod.yml --env-file .env.production logs --tail=100
   ```

3. **Actualizaciones**: Para actualizar el código en el futuro:
   ```bash
   cd ~/drtc_certificados
   git pull origin main
   docker compose -f docker-compose.prod.yml --env-file .env.production build web
   docker compose -f docker-compose.prod.yml --env-file .env.production up -d
   ```

4. **Seguridad**: Cambia las credenciales por defecto:
   - Usuario admin
   - Contraseñas de base de datos
   - SECRET_KEY de Django

---

## 🎯 Resumen de URLs

- **Admin:** http://161.132.47.92:7070/admin/
- **API:** http://161.132.47.92:7070/api/
- **Health Check:** http://161.132.47.92:7070/health/
- **Consulta Pública:** http://161.132.47.92:7070/

---

**¡Listo para desplegar!** 🚀

Sigue los pasos en orden y verifica cada uno antes de continuar al siguiente.
