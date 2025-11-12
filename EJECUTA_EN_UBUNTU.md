# 🚀 Ejecuta Esto en Tu Servidor Ubuntu

## 📍 Tu Situación

- ✅ Servidor Ubuntu
- ✅ Repositorio ya clonado de GitHub
- ✅ Necesitas actualizar con últimos cambios
- ✅ Dominio: `certificados.transportespuno.gob.pe`

---

## ⚡ OPCIÓN 1: Script Automatizado (MÁS FÁCIL)

### Paso 1: Dar Permisos al Script

```bash
chmod +x deploy-ubuntu.sh
```

### Paso 2: Ejecutar

```bash
./deploy-ubuntu.sh
```

El script hará todo automáticamente:
- ✅ Actualiza código desde GitHub
- ✅ Verifica configuración
- ✅ Construye imágenes
- ✅ Despliega servicios
- ✅ Verifica que todo funcione

---

## 🔧 OPCIÓN 2: Comandos Manuales (Paso a Paso)

### 1. Actualizar Código desde GitHub

```bash
# Ver estado actual
git status

# Actualizar
git pull origin main
```

### 2. Configurar Variables de Entorno

```bash
# Si no existe .env.production, crearlo
cp .env.production.example .env.production

# Editar con tus valores
nano .env.production
```

**Valores importantes a configurar:**
```env
SECRET_KEY=genera-una-clave-unica-aqui
DB_PASSWORD=tu-password-postgresql
DJANGO_SUPERUSER_PASSWORD=tu-password-admin
ALLOWED_HOSTS=certificados.transportespuno.gob.pe,localhost,127.0.0.1
SITE_URL=https://certificados.transportespuno.gob.pe
```

**Generar SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 3. Desplegar

```bash
# Detener servicios anteriores
docker compose -f docker-compose.prod.yml down

# Construir imagen
docker compose -f docker-compose.prod.yml build --no-cache web

# Iniciar servicios
docker compose -f docker-compose.prod.yml up -d
```

### 4. Verificar

```bash
# Ver estado
docker compose -f docker-compose.prod.yml ps

# Ver logs
docker compose -f docker-compose.prod.yml logs -f
```

Presiona `Ctrl+C` para salir de los logs.

---

## ✅ Verificación Rápida

```bash
# 1. Estado de servicios
docker compose -f docker-compose.prod.yml ps

# 2. Health check
curl http://localhost/health/

# 3. Ver logs
docker compose -f docker-compose.prod.yml logs --tail=50
```

**Deberías ver:**
- Todos los servicios "Up" o "Up (healthy)"
- Health check responde con status "healthy"
- Logs sin errores críticos

---

## 🌐 Acceder a la Aplicación

### Desde el Servidor

```bash
curl http://localhost/
curl http://localhost/health/
```

### Desde tu Navegador

Si tu servidor tiene IP pública:
- http://TU_IP_SERVIDOR/
- http://TU_IP_SERVIDOR/admin/

Con dominio configurado:
- https://certificados.transportespuno.gob.pe/
- https://certificados.transportespuno.gob.pe/admin/

---

## 🔐 Configurar SSL/HTTPS (Recomendado)

### 1. Instalar Certbot

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Obtener Certificado

```bash
# Detener nginx temporalmente
docker compose -f docker-compose.prod.yml stop nginx

# Obtener certificado
sudo certbot certonly --standalone -d certificados.transportespuno.gob.pe

# Reiniciar nginx
docker compose -f docker-compose.prod.yml start nginx
```

### 3. Actualizar .env.production

```bash
nano .env.production
```

Cambiar:
```env
SITE_URL=https://certificados.transportespuno.gob.pe
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 4. Reiniciar

```bash
docker compose -f docker-compose.prod.yml restart
```

---

## 📊 Comandos Útiles del Día a Día

```bash
# Ver estado
docker compose -f docker-compose.prod.yml ps

# Ver logs
docker compose -f docker-compose.prod.yml logs -f

# Reiniciar
docker compose -f docker-compose.prod.yml restart

# Backup de BD
docker compose -f docker-compose.prod.yml exec db pg_dump -U certificados_user certificados_prod > backup.sql

# Actualizar aplicación
git pull origin main
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d
```

---

## 🚨 Si Algo Sale Mal

### Ver Logs Detallados

```bash
docker compose -f docker-compose.prod.yml logs --tail=200
```

### Reiniciar Todo

```bash
docker compose -f docker-compose.prod.yml restart
```

### Reconstruir Completamente

```bash
docker compose -f docker-compose.prod.yml down -v
docker system prune -f
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

---

## 📚 Documentación Completa

Para más detalles, consulta:

1. **`DESPLIEGUE_UBUNTU.md`** - Guía completa para Ubuntu
2. **`COMANDOS_UBUNTU.md`** - Referencia de comandos
3. **`PASOS_FINALES.md`** - Guía paso a paso completa

---

## 🎯 Resumen de Archivos Actualizados

Los últimos cambios en GitHub incluyen:

- ✅ **Dockerfile** - Permisos de entrypoint.sh corregidos
- ✅ **Scripts** - Actualizados a Docker Compose v2
- ✅ **Variables** - Dominio transportespuno.gob.pe configurado
- ✅ **Documentación** - Guías completas creadas

---

## ✨ Próximos Pasos

1. **Ahora:** Ejecuta `./deploy-ubuntu.sh` o los comandos manuales
2. **Verifica:** Que todo funcione correctamente
3. **Configura SSL:** Para HTTPS (recomendado)
4. **Configura DNS:** Para que el dominio apunte a tu servidor
5. **Haz Backup:** Configura backups automáticos

---

## 💡 Tip: Crear Alias

Para facilitar los comandos, agrega esto a tu `~/.bashrc`:

```bash
echo "alias dcp='docker compose -f docker-compose.prod.yml'" >> ~/.bashrc
echo "alias dcps='docker compose -f docker-compose.prod.yml ps'" >> ~/.bashrc
echo "alias dcl='docker compose -f docker-compose.prod.yml logs -f'" >> ~/.bashrc
source ~/.bashrc
```

Ahora puedes usar:
```bash
dcp ps    # Ver estado
dcl       # Ver logs
```

---

**¡Listo para desplegar! 🚀**

Ejecuta:
```bash
./deploy-ubuntu.sh
```

O sigue los comandos manuales arriba.

---

**Sistema:** Ubuntu Server  
**Docker Compose:** v2 (sin guión)  
**Dominio:** certificados.transportespuno.gob.pe  
**Estado:** ✅ Listo para desplegar
