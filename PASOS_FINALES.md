# ✅ Pasos Finales - Actualización y Despliegue

## 📋 Resumen de Cambios Realizados

### 1. ✅ Dockerfile Actualizado
- Permisos de `entrypoint.sh` corregidos
- Error "permission denied" solucionado

### 2. ✅ Scripts Actualizados a Docker Compose v2
- Todos los scripts usan `docker compose` (sin guión)
- `deploy-production.bat`
- `EJECUTA_ESTOS_COMANDOS.bat`
- Toda la documentación

### 3. ✅ Dominio Configurado
- Dominio: `certificados.transportespuno.gob.pe`
- `.env.production` actualizado
- `.env.production.example` actualizado
- Emails institucionales actualizados

### 4. ✅ Documentación Completa
- 10+ archivos de guías y referencias
- Scripts automatizados
- Comandos actualizados

---

## 🚀 PASO 1: Actualizar GitHub

### Opción A: Script Automatizado (Recomendado)

```cmd
actualizar-github.bat
```

### Opción B: Comandos Manuales

```cmd
git add .
git commit -m "Actualización: Docker Compose v2, corrección permisos, dominio transportespuno.gob.pe"
git push origin main
```

---

## 🐳 PASO 2: Desplegar Localmente (Prueba)

### Opción A: Script Automatizado

```cmd
EJECUTA_ESTOS_COMANDOS.bat
```

### Opción B: Comandos Manuales

```cmd
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache web
docker compose -f docker-compose.prod.yml up -d
```

### Verificar

```cmd
docker compose -f docker-compose.prod.yml ps
```

Abrir en navegador:
- http://localhost/
- http://localhost/admin/

---

## 🌐 PASO 3: Configurar Dominio (En Servidor)

### A. Configurar DNS

En tu proveedor de DNS (GoDaddy, Cloudflare, etc.):

```
Tipo: A
Host: certificados
Dominio: transportespuno.gob.pe
Valor: [IP_DEL_SERVIDOR]
TTL: 3600
```

Resultado: `certificados.transportespuno.gob.pe` → IP del servidor

### B. Verificar DNS

```cmd
nslookup certificados.transportespuno.gob.pe
```

O:

```cmd
ping certificados.transportespuno.gob.pe
```

---

## 🖥️ PASO 4: Desplegar en Servidor

### A. Conectar al Servidor

```bash
ssh usuario@servidor
```

### B. Clonar o Actualizar Repositorio

**Si es primera vez:**
```bash
cd /var/www
git clone https://github.com/TU_USUARIO/TU_REPO.git certificados
cd certificados
```

**Si ya existe:**
```bash
cd /var/www/certificados
git pull origin main
```

### C. Configurar Variables de Entorno

```bash
# Copiar ejemplo
cp .env.production.example .env.production

# Editar con valores reales
nano .env.production
```

Configurar:
- `SECRET_KEY` - Generar uno único
- `DB_PASSWORD` - Contraseña segura
- `DJANGO_SUPERUSER_PASSWORD` - Contraseña de admin
- `SITE_URL=https://certificados.transportespuno.gob.pe`
- `SECURE_SSL_REDIRECT=True` (cuando tengas SSL)

### D. Desplegar

```bash
# Construir y desplegar
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d

# Verificar
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

---

## 🔐 PASO 5: Configurar SSL/HTTPS

### A. Instalar Certbot

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

### B. Obtener Certificado

```bash
sudo certbot --nginx -d certificados.transportespuno.gob.pe
```

### C. Actualizar .env.production

```bash
nano .env.production
```

Cambiar:
```env
SITE_URL=https://certificados.transportespuno.gob.pe
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

### D. Reiniciar Servicios

```bash
docker compose -f docker-compose.prod.yml restart
```

---

## ✅ PASO 6: Verificación Final

### A. Verificar Servicios

```bash
docker compose -f docker-compose.prod.yml ps
```

Todos deben estar "Up" o "Up (healthy)".

### B. Verificar Acceso Web

Abrir en navegador:
- https://certificados.transportespuno.gob.pe/
- https://certificados.transportespuno.gob.pe/admin/
- https://certificados.transportespuno.gob.pe/health/

### C. Verificar Logs

```bash
docker compose -f docker-compose.prod.yml logs --tail=100
```

No debe haber errores críticos.

### D. Verificar Base de Datos

```bash
docker compose -f docker-compose.prod.yml exec db psql -U certificados_user -d certificados_prod -c "\dt"
```

### E. Verificar Redis

```bash
docker compose -f docker-compose.prod.yml exec redis redis-cli PING
```

Debe responder "PONG".

---

## 📊 Checklist Completo

### Actualización Local
- [ ] Ejecutar `actualizar-github.bat`
- [ ] Verificar push exitoso en GitHub
- [ ] Probar despliegue local con `EJECUTA_ESTOS_COMANDOS.bat`
- [ ] Verificar que funciona en http://localhost/

### Configuración de Servidor
- [ ] DNS configurado para certificados.transportespuno.gob.pe
- [ ] DNS propagado (verificar con nslookup)
- [ ] Servidor accesible por SSH
- [ ] Docker y Docker Compose instalados en servidor

### Despliegue en Servidor
- [ ] Repositorio clonado/actualizado
- [ ] `.env.production` configurado con valores reales
- [ ] Servicios desplegados con docker compose
- [ ] Todos los contenedores corriendo
- [ ] Sin errores en logs

### SSL/HTTPS
- [ ] Certbot instalado
- [ ] Certificado SSL obtenido
- [ ] `.env.production` actualizado para HTTPS
- [ ] Servicios reiniciados
- [ ] HTTPS funcionando

### Verificación Final
- [ ] Sitio accesible en https://certificados.transportespuno.gob.pe/
- [ ] Admin accesible
- [ ] Health check respondiendo
- [ ] Base de datos funcionando
- [ ] Redis funcionando
- [ ] Logs sin errores críticos

---

## 🎯 Comandos Rápidos de Referencia

### Local (Windows)
```cmd
REM Actualizar GitHub
actualizar-github.bat

REM Desplegar localmente
EJECUTA_ESTOS_COMANDOS.bat

REM Ver estado
docker compose -f docker-compose.prod.yml ps

REM Ver logs
docker compose -f docker-compose.prod.yml logs -f
```

### Servidor (Linux)
```bash
# Actualizar código
git pull origin main

# Reconstruir y desplegar
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d

# Ver estado
docker compose -f docker-compose.prod.yml ps

# Ver logs
docker compose -f docker-compose.prod.yml logs -f

# Backup de BD
docker compose -f docker-compose.prod.yml exec db pg_dump -U certificados_user certificados_prod > backup.sql
```

---

## 📞 Soporte

### Documentación Disponible

1. **`README_DESPLIEGUE.md`** - Guía principal
2. **`GUIA_ACTUALIZACION_GITHUB.md`** - Actualizar GitHub
3. **`COMANDOS_PRODUCCION_2025.md`** - Referencia de comandos
4. **`DESPLEGAR_AHORA.md`** - Comandos rápidos
5. **`CHECKLIST_DESPLIEGUE.md`** - Checklist detallado

### Scripts Disponibles

1. **`actualizar-github.bat`** - Actualizar repositorio
2. **`EJECUTA_ESTOS_COMANDOS.bat`** - Desplegar localmente
3. **`deploy-production.bat`** - Despliegue completo

---

## 🎉 ¡Listo!

Siguiendo estos pasos tendrás:

✅ Código actualizado en GitHub  
✅ Dominio configurado correctamente  
✅ Aplicación desplegada en servidor  
✅ SSL/HTTPS configurado  
✅ Sistema en producción funcionando  

**Dominio final:** https://certificados.transportespuno.gob.pe/

---

**Última actualización:** 2025-11-10  
**Dominio:** certificados.transportespuno.gob.pe  
**Docker Compose:** v2 (sin guión)  
**Estado:** ✅ Listo para desplegar
