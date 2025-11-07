# 🚀 GUÍA COMPLETA: DESPLIEGUE EN LA NUBE

## 📋 INFORMACIÓN IMPORTANTE
- **Puerto HTTP:** 8181 (en lugar de 80)
- **Puerto HTTPS:** 8443 (en lugar de 443)
- **Acceso:** http://TU_IP:8181 o https://TU_DOMINIO:8443

---

## 🎯 OPCIONES DE NUBE

### Opción 1: VPS/Servidor Dedicado (Recomendado)
- DigitalOcean Droplet
- AWS EC2
- Google Cloud Compute Engine
- Azure Virtual Machine
- Linode
- Vultr

### Opción 2: Servidor Propio
- Servidor físico con IP pública
- Conexión estable a internet

---

## 📦 REQUISITOS DEL SERVIDOR

### Mínimos:
- **CPU:** 2 cores
- **RAM:** 2 GB
- **Disco:** 20 GB SSD
- **OS:** Ubuntu 22.04 LTS (recomendado)
- **Red:** IP pública estática

### Recomendados:
- **CPU:** 4 cores
- **RAM:** 4 GB
- **Disco:** 40 GB SSD
- **OS:** Ubuntu 22.04 LTS

---

## 🔧 PASO 1: PREPARAR EL SERVIDOR

### 1.1 Conectarse al Servidor
```bash
# Desde tu computadora local
ssh root@TU_IP_SERVIDOR

# O si tienes usuario diferente
ssh usuario@TU_IP_SERVIDOR
```

### 1.2 Actualizar Sistema
```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y curl git wget
```

### 1.3 Instalar Docker
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt-get install -y docker-compose-plugin

# Agregar usuario al grupo docker (opcional)
sudo usermod -aG docker $USER

# Aplicar cambios (cerrar y volver a conectar SSH)
exit
ssh root@TU_IP_SERVIDOR
```

### 1.4 Verificar Instalación
```bash
docker --version
docker compose version
```

---

## 📥 PASO 2: CLONAR EL PROYECTO

```bash
# Ir al directorio home
cd ~

# Clonar repositorio
git clone https://github.com/ajahuanex/sistema_certificados_drtc.git

# Entrar al directorio
cd sistema_certificados_drtc

# Verificar archivos
ls -la
```

---

## 🔐 PASO 3: CONFIGURAR SEGURIDAD

### 3.1 Generar SECRET_KEY Seguro
```bash
# Generar clave aleatoria
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# Copiar el resultado, lo usarás en el siguiente paso
```

### 3.2 Crear Archivo .env.production
```bash
# Copiar ejemplo
cp .env.production.example .env.production

# Editar con nano
nano .env.production
```

### 3.3 Configurar Variables (IMPORTANTE)
Edita el archivo `.env.production` con estos valores:

```bash
# DJANGO
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
SECRET_KEY=PEGA_AQUI_LA_CLAVE_QUE_GENERASTE_EN_3.1

# Hosts - Cambia por tu IP o dominio
ALLOWED_HOSTS=TU_IP_SERVIDOR,TU_DOMINIO.COM

# URLs - Cambia por tu IP o dominio
SITE_URL=http://TU_IP_SERVIDOR:8181
ADMIN_URL=admin/

# BASE DE DATOS - CAMBIA LA CONTRASEÑA
DB_ENGINE=django.db.backends.postgresql
DB_NAME=certificados_prod
DB_USER=certificados_user
DB_PASSWORD=CAMBIA_ESTA_CONTRASEÑA_POR_UNA_SEGURA_123456
DB_HOST=db
DB_PORT=5432

# REDIS
REDIS_URL=redis://redis:6379/0

# EMAIL (opcional por ahora)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=Sistema de Certificados DRTC <certificados@drtc.gob.pe>

# ARCHIVOS
STATIC_URL=/static/
STATIC_ROOT=/app/staticfiles
MEDIA_URL=/media/
MEDIA_ROOT=/app/media

# INSTITUCIÓN
INSTITUTION_NAME=Dirección Regional de Trabajo y Promoción del Empleo - Puno
INSTITUTION_SHORT_NAME=DRTC Puno
INSTITUTION_ADDRESS=Jr. Deustua 356, Puno, Perú
INSTITUTION_PHONE=+51 51 351234
INSTITUTION_EMAIL=info@drtc.gob.pe

# PERFORMANCE
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=300

# HEALTH CHECKS
HEALTH_CHECK_ENABLED=True

# SEGURIDAD SSL (False por ahora, True cuando tengas SSL)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
SECURE_HSTS_SECONDS=0
```

**Guardar:** Ctrl+O, Enter, Ctrl+X

---

## 🔥 PASO 4: CONFIGURAR FIREWALL

```bash
# Instalar UFW si no está instalado
sudo apt-get install -y ufw

# Permitir SSH (IMPORTANTE - no te bloquees)
sudo ufw allow 22/tcp

# Permitir puerto 8181 (HTTP)
sudo ufw allow 8181/tcp

# Permitir puerto 8443 (HTTPS) - para futuro
sudo ufw allow 8443/tcp

# Habilitar firewall
sudo ufw enable

# Verificar estado
sudo ufw status
```

---

## 🐳 PASO 5: CONSTRUIR Y DESPLEGAR

### 5.1 Construir Imágenes
```bash
# Construir desde cero
docker compose -f docker-compose.prod.yml build --no-cache
```

Esto tomará 3-5 minutos.

### 5.2 Iniciar Servicios
```bash
# Iniciar todos los contenedores
docker compose -f docker-compose.prod.yml up -d
```

### 5.3 Verificar Estado
```bash
# Ver estado de contenedores
docker compose -f docker-compose.prod.yml ps

# Deberías ver:
# certificados_db_prod      healthy
# certificados_redis_prod   healthy
# certificados_web_prod     healthy
# certificados_nginx_prod   healthy
```

### 5.4 Ver Logs (si hay problemas)
```bash
# Ver logs de todos los servicios
docker compose -f docker-compose.prod.yml logs -f

# Ver logs de un servicio específico
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f db
```

---

## 👤 PASO 6: CREAR SUPERUSUARIO

### Opción A: Con Contraseña en Variable
```bash
# Exportar contraseña
export DJANGO_SUPERUSER_PASSWORD="TuContraseñaSegura123!"

# Crear superusuario
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser \
  --noinput \
  --username admin \
  --email admin@drtc.gob.pe
```

### Opción B: Interactivo
```bash
# Crear superusuario interactivamente
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Seguir las instrucciones:
# Username: admin
# Email: admin@drtc.gob.pe
# Password: (tu contraseña segura)
# Password (again): (repetir)
```

---

## 🧪 PASO 7: PROBAR EL SISTEMA

### 7.1 Health Check
```bash
# Desde el servidor
curl http://localhost:8181/health/

# Debería responder: {"status": "healthy"}
```

### 7.2 Desde tu Navegador
Abre en tu navegador:

```
http://TU_IP_SERVIDOR:8181
http://TU_IP_SERVIDOR:8181/admin/
http://TU_IP_SERVIDOR:8181/health/
```

**Ejemplo:** Si tu IP es 192.168.1.100:
- http://192.168.1.100:8181
- http://192.168.1.100:8181/admin/

---

## 🔧 COMANDOS ÚTILES

### Ver Estado
```bash
docker compose -f docker-compose.prod.yml ps
```

### Ver Logs
```bash
# Todos los servicios
docker compose -f docker-compose.prod.yml logs -f

# Solo web
docker compose -f docker-compose.prod.yml logs -f web

# Últimas 50 líneas
docker compose -f docker-compose.prod.yml logs --tail=50 web
```

### Reiniciar Servicios
```bash
# Reiniciar todo
docker compose -f docker-compose.prod.yml restart

# Reiniciar solo web
docker compose -f docker-compose.prod.yml restart web
```

### Detener Sistema
```bash
docker compose -f docker-compose.prod.yml down
```

### Actualizar Código
```bash
# Detener servicios
docker compose -f docker-compose.prod.yml down

# Actualizar código
git pull origin main

# Reconstruir y reiniciar
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

### Backup de Base de Datos
```bash
# Crear backup
docker compose -f docker-compose.prod.yml exec db pg_dump \
  -U certificados_user \
  certificados_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Comprimir
gzip backup_*.sql
```

### Restaurar Base de Datos
```bash
# Descomprimir
gunzip backup_FECHA.sql.gz

# Restaurar
docker compose -f docker-compose.prod.yml exec -T db psql \
  -U certificados_user \
  certificados_prod < backup_FECHA.sql
```

---

## 🌐 PASO 8: CONFIGURAR DOMINIO (OPCIONAL)

Si tienes un dominio (ej: certificados.drtc.gob.pe):

### 8.1 Configurar DNS
En tu proveedor de DNS:

```
Tipo    Nombre                      Valor               TTL
A       certificados.drtc.gob.pe    TU_IP_SERVIDOR     3600
```

### 8.2 Actualizar .env.production
```bash
nano .env.production

# Cambiar:
ALLOWED_HOSTS=TU_IP_SERVIDOR,certificados.drtc.gob.pe
SITE_URL=http://certificados.drtc.gob.pe:8181
```

### 8.3 Reiniciar
```bash
docker compose -f docker-compose.prod.yml restart web
```

### 8.4 Acceder
```
http://certificados.drtc.gob.pe:8181
```

---

## 🔒 PASO 9: CONFIGURAR SSL/HTTPS (OPCIONAL)

### 9.1 Instalar Certbot
```bash
sudo apt-get install -y certbot
```

### 9.2 Detener Nginx Temporalmente
```bash
docker compose -f docker-compose.prod.yml stop nginx
```

### 9.3 Obtener Certificado
```bash
sudo certbot certonly --standalone \
  -d certificados.drtc.gob.pe \
  --preferred-challenges http \
  --http-01-port 8181
```

### 9.4 Copiar Certificados
```bash
# Crear carpeta
mkdir -p ssl

# Copiar certificados
sudo cp /etc/letsencrypt/live/certificados.drtc.gob.pe/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/certificados.drtc.gob.pe/privkey.pem ssl/key.pem

# Dar permisos
sudo chown $USER:$USER ssl/*.pem
```

### 9.5 Descomentar HTTPS en nginx.prod.conf
```bash
nano nginx.prod.conf

# Buscar las líneas que empiezan con:
# # server {
# #     listen 443 ssl http2;

# Quitar los comentarios (#) de toda esa sección
```

### 9.6 Actualizar .env.production
```bash
nano .env.production

# Cambiar a True:
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

# Cambiar URL:
SITE_URL=https://certificados.drtc.gob.pe:8443
```

### 9.7 Reiniciar
```bash
docker compose -f docker-compose.prod.yml restart
```

### 9.8 Acceder con HTTPS
```
https://certificados.drtc.gob.pe:8443
```

---

## 🔍 SOLUCIÓN DE PROBLEMAS

### Problema: Contenedor web no inicia
```bash
# Ver logs
docker compose -f docker-compose.prod.yml logs web

# Verificar variables de entorno
docker compose -f docker-compose.prod.yml exec web env | grep DB
```

### Problema: Error de base de datos
```bash
# Conectar a PostgreSQL
docker compose -f docker-compose.prod.yml exec db psql -U postgres

# Crear usuario manualmente
CREATE USER certificados_user WITH PASSWORD 'tu_contraseña';
CREATE DATABASE certificados_prod OWNER certificados_user;
GRANT ALL PRIVILEGES ON DATABASE certificados_prod TO certificados_user;
\q

# Reiniciar web
docker compose -f docker-compose.prod.yml restart web
```

### Problema: No puedo acceder desde internet
```bash
# Verificar firewall
sudo ufw status

# Verificar que nginx está escuchando
docker compose -f docker-compose.prod.yml exec nginx netstat -tlnp

# Verificar desde el servidor
curl http://localhost:8181/health/
```

### Problema: Archivos estáticos no cargan
```bash
# Recopilar archivos estáticos
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Reiniciar nginx
docker compose -f docker-compose.prod.yml restart nginx
```

---

## 📊 MONITOREO

### Ver Uso de Recursos
```bash
# CPU y memoria de contenedores
docker stats

# Espacio en disco
df -h

# Logs del sistema
sudo journalctl -u docker -f
```

### Configurar Backups Automáticos
```bash
# Crear script de backup
nano ~/backup.sh
```

Contenido del script:
```bash
#!/bin/bash
cd ~/sistema_certificados_drtc
docker compose -f docker-compose.prod.yml exec -T db pg_dump \
  -U certificados_user \
  certificados_prod > ~/backups/backup_$(date +%Y%m%d_%H%M%S).sql
gzip ~/backups/backup_*.sql
find ~/backups -name "backup_*.sql.gz" -mtime +7 -delete
```

```bash
# Dar permisos
chmod +x ~/backup.sh

# Crear carpeta de backups
mkdir -p ~/backups

# Agregar a crontab (backup diario a las 2 AM)
crontab -e

# Agregar esta línea:
0 2 * * * /root/backup.sh
```

---

## ✅ CHECKLIST FINAL

- [ ] Servidor actualizado
- [ ] Docker y Docker Compose instalados
- [ ] Proyecto clonado
- [ ] .env.production configurado con valores seguros
- [ ] Firewall configurado (puerto 8181)
- [ ] Contenedores construidos
- [ ] Servicios iniciados y saludables
- [ ] Superusuario creado
- [ ] Sistema accesible desde navegador
- [ ] Backups configurados (opcional)
- [ ] SSL configurado (opcional)

---

## 🎉 ¡LISTO!

Tu sistema está desplegado en:
- **HTTP:** http://TU_IP:8181
- **Admin:** http://TU_IP:8181/admin/
- **HTTPS:** https://TU_DOMINIO:8443 (si configuraste SSL)

---

## 📞 SOPORTE

Si tienes problemas:
1. Revisa los logs: `docker compose -f docker-compose.prod.yml logs -f`
2. Verifica el estado: `docker compose -f docker-compose.prod.yml ps`
3. Revisa la documentación en el repositorio

---

**Creado:** 2025-11-07  
**Puerto HTTP:** 8181  
**Puerto HTTPS:** 8443  
**Estado:** ✅ Listo para desplegar
