# 🐧 Despliegue en Ubuntu Server - Guía Completa

## 📋 Situación Actual

- ✅ Estás en un servidor Ubuntu
- ✅ Ya clonaste el repositorio de GitHub
- ✅ Necesitas actualizar con los últimos cambios
- ✅ Dominio: `certificados.transportespuno.gob.pe`

---

## 🚀 PASO 1: Actualizar Repositorio desde GitHub

### A. Verificar Estado Actual

```bash
# Ver en qué directorio estás
pwd

# Ver estado del repositorio
git status

# Ver rama actual
git branch
```

### B. Hacer Pull de los Últimos Cambios

```bash
# Guardar cambios locales si los hay
git stash

# Actualizar desde GitHub
git pull origin main

# O si tu rama es master:
git pull origin master

# Restaurar cambios locales si los guardaste
git stash pop
```

### C. Verificar Archivos Actualizados

```bash
# Ver últimos commits
git log --oneline -5

# Ver archivos modificados
git diff HEAD~1
```

---

## ⚙️ PASO 2: Configurar Variables de Entorno

### A. Copiar Archivo de Ejemplo

```bash
# Si no existe .env.production, crearlo desde el ejemplo
cp .env.production.example .env.production
```

### B. Editar Variables de Entorno

```bash
# Editar con nano
nano .env.production

# O con vim
vim .env.production
```

### C. Configuración Mínima Requerida

Actualiza estos valores en `.env.production`:

```env
# Django
SECRET_KEY=genera-una-clave-secreta-unica-aqui-de-50-caracteres-minimo
DEBUG=False
ALLOWED_HOSTS=certificados.transportespuno.gob.pe,www.certificados.transportespuno.gob.pe,localhost,127.0.0.1

# URLs
SITE_URL=https://certificados.transportespuno.gob.pe

# Base de datos
DB_PASSWORD=tu-password-seguro-para-postgresql

# Superusuario
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@transportespuno.gob.pe
DJANGO_SUPERUSER_PASSWORD=tu-password-admin-seguro

# HTTPS (activar cuando tengas SSL)
SECURE_SSL_REDIRECT=False  # Cambiar a True cuando tengas SSL
SESSION_COOKIE_SECURE=False  # Cambiar a True cuando tengas SSL
CSRF_COOKIE_SECURE=False  # Cambiar a True cuando tengas SSL

# CSRF y CORS
CSRF_TRUSTED_ORIGINS=https://certificados.transportespuno.gob.pe
CORS_ALLOWED_ORIGINS=https://certificados.transportespuno.gob.pe
```

### D. Generar SECRET_KEY Seguro

```bash
# Opción 1: Usando Python
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# Opción 2: Usando OpenSSL
openssl rand -base64 50
```

Copia el resultado y pégalo en `SECRET_KEY` en `.env.production`.

---

## 🐳 PASO 3: Verificar Docker

### A. Verificar Instalación

```bash
# Verificar Docker
docker --version

# Verificar Docker Compose
docker compose version
```

### B. Si Docker No Está Instalado

```bash
# Actualizar sistema
sudo apt update
sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Aplicar cambios (o cerrar sesión y volver a entrar)
newgrp docker

# Verificar
docker --version
docker compose version
```

---

## 🚀 PASO 4: Desplegar Aplicación

### A. Detener Servicios Anteriores (si existen)

```bash
docker compose -f docker-compose.prod.yml down
```

### B. Construir Imágenes

```bash
# Construir sin caché para asegurar cambios
docker compose -f docker-compose.prod.yml build --no-cache
```

### C. Iniciar Servicios

```bash
# Iniciar en segundo plano
docker compose -f docker-compose.prod.yml up -d
```

### D. Verificar Estado

```bash
# Ver estado de contenedores
docker compose -f docker-compose.prod.yml ps

# Ver logs
docker compose -f docker-compose.prod.yml logs -f
```

Presiona `Ctrl+C` para salir de los logs.

---

## ✅ PASO 5: Verificación

### A. Verificar Servicios

```bash
# Estado de todos los servicios
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

### B. Verificar Logs

```bash
# Logs de todos los servicios
docker compose -f docker-compose.prod.yml logs --tail=50

# Logs solo del servicio web
docker compose -f docker-compose.prod.yml logs web --tail=50

# Logs en tiempo real
docker compose -f docker-compose.prod.yml logs -f
```

### C. Verificar Base de Datos

```bash
# Conectar a PostgreSQL
docker compose -f docker-compose.prod.yml exec db psql -U certificados_user -d certificados_prod

# Dentro de psql:
\dt  # Listar tablas
\q   # Salir
```

### D. Verificar Redis

```bash
# Conectar a Redis
docker compose -f docker-compose.prod.yml exec redis redis-cli

# Dentro de redis-cli:
PING  # Debe responder PONG
exit
```

### E. Verificar Health Check

```bash
# Desde el servidor
curl http://localhost/health/

# O ver en navegador (si tienes IP pública)
# http://TU_IP_SERVIDOR/health/
```

---

## 🌐 PASO 6: Configurar Firewall

### A. Permitir Puertos Necesarios

```bash
# Permitir HTTP
sudo ufw allow 80/tcp

# Permitir HTTPS
sudo ufw allow 443/tcp

# Permitir SSH (si no está permitido)
sudo ufw allow 22/tcp

# Habilitar firewall
sudo ufw enable

# Ver estado
sudo ufw status
```

---

## 🔐 PASO 7: Configurar SSL/HTTPS (Opcional pero Recomendado)

### A. Instalar Certbot

```bash
# Instalar Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

### B. Obtener Certificado SSL

```bash
# Detener nginx temporalmente
docker compose -f docker-compose.prod.yml stop nginx

# Obtener certificado
sudo certbot certonly --standalone -d certificados.transportespuno.gob.pe

# Reiniciar nginx
docker compose -f docker-compose.prod.yml start nginx
```

### C. Configurar Renovación Automática

```bash
# Probar renovación
sudo certbot renew --dry-run

# Certbot configurará renovación automática
```

### D. Actualizar .env.production para HTTPS

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

### E. Reiniciar Servicios

```bash
docker compose -f docker-compose.prod.yml restart
```

---

## 📊 Comandos Útiles

### Gestión de Servicios

```bash
# Ver estado
docker compose -f docker-compose.prod.yml ps

# Ver logs
docker compose -f docker-compose.prod.yml logs -f

# Reiniciar todos los servicios
docker compose -f docker-compose.prod.yml restart

# Reiniciar un servicio específico
docker compose -f docker-compose.prod.yml restart web

# Detener servicios
docker compose -f docker-compose.prod.yml stop

# Iniciar servicios detenidos
docker compose -f docker-compose.prod.yml start

# Detener y eliminar todo
docker compose -f docker-compose.prod.yml down

# Detener y eliminar con volúmenes
docker compose -f docker-compose.prod.yml down -v
```

### Comandos Django

```bash
# Ejecutar migraciones
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Crear superusuario
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Recopilar archivos estáticos
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Shell de Django
docker compose -f docker-compose.prod.yml exec web python manage.py shell

# Ver usuarios
docker compose -f docker-compose.prod.yml exec web python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.all())"
```

### Backup

```bash
# Backup de base de datos
docker compose -f docker-compose.prod.yml exec db pg_dump -U certificados_user certificados_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore de base de datos
docker compose -f docker-compose.prod.yml exec -T db psql -U certificados_user certificados_prod < backup.sql

# Backup de archivos media
docker cp certificados_web_prod:/app/media ./media_backup_$(date +%Y%m%d)
```

### Monitoreo

```bash
# Ver uso de recursos
docker stats

# Ver procesos en un contenedor
docker compose -f docker-compose.prod.yml exec web ps aux

# Ver espacio en disco
df -h

# Ver logs del sistema
sudo journalctl -u docker -f
```

---

## 🔄 Actualizar Aplicación

Cuando hagas cambios en GitHub y quieras actualizar el servidor:

```bash
# 1. Hacer pull de cambios
git pull origin main

# 2. Reconstruir imagen
docker compose -f docker-compose.prod.yml build --no-cache web

# 3. Reiniciar servicios
docker compose -f docker-compose.prod.yml up -d

# 4. Ver logs para verificar
docker compose -f docker-compose.prod.yml logs -f web
```

---

## 🚨 Troubleshooting

### Error: "Permission denied" en entrypoint.sh

Ya está solucionado en el Dockerfile actualizado. Solo necesitas reconstruir:

```bash
docker compose -f docker-compose.prod.yml build --no-cache web
docker compose -f docker-compose.prod.yml up -d
```

### Error: "Port already in use"

```bash
# Ver qué está usando el puerto 80
sudo lsof -i :80

# Detener el servicio que lo usa
sudo systemctl stop apache2  # Si es Apache
sudo systemctl stop nginx    # Si es Nginx

# O cambiar puerto en docker-compose.prod.yml
```

### Error: "Cannot connect to Docker daemon"

```bash
# Iniciar Docker
sudo systemctl start docker

# Habilitar Docker al inicio
sudo systemctl enable docker

# Verificar estado
sudo systemctl status docker
```

### Contenedores se reinician constantemente

```bash
# Ver logs detallados
docker compose -f docker-compose.prod.yml logs web --tail=200

# Ver por qué se reinicia
docker inspect certificados_web_prod
```

### Limpiar y empezar de nuevo

```bash
# Detener todo
docker compose -f docker-compose.prod.yml down -v

# Limpiar sistema Docker
docker system prune -a -f
docker volume prune -f

# Reconstruir desde cero
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

---

## 📝 Script de Despliegue Rápido

Crea un script para desplegar rápidamente:

```bash
# Crear script
nano deploy.sh
```

Contenido:

```bash
#!/bin/bash
set -e

echo "🚀 Desplegando aplicación..."

# Actualizar código
echo "📥 Actualizando código desde GitHub..."
git pull origin main

# Reconstruir imagen
echo "🔨 Reconstruyendo imagen..."
docker compose -f docker-compose.prod.yml build --no-cache web

# Reiniciar servicios
echo "🔄 Reiniciando servicios..."
docker compose -f docker-compose.prod.yml up -d

# Esperar un momento
sleep 5

# Verificar estado
echo "✅ Verificando estado..."
docker compose -f docker-compose.prod.yml ps

echo "🎉 Despliegue completado!"
echo "Ver logs: docker compose -f docker-compose.prod.yml logs -f"
```

Dar permisos y ejecutar:

```bash
chmod +x deploy.sh
./deploy.sh
```

---

## ✅ Checklist de Despliegue

- [ ] Repositorio actualizado con `git pull`
- [ ] `.env.production` configurado con valores correctos
- [ ] Docker y Docker Compose instalados
- [ ] Firewall configurado (puertos 80, 443)
- [ ] Servicios desplegados con `docker compose up -d`
- [ ] Todos los contenedores corriendo (verificar con `ps`)
- [ ] Logs sin errores críticos
- [ ] Health check respondiendo
- [ ] Sitio accesible desde navegador
- [ ] SSL/HTTPS configurado (opcional)
- [ ] Backup configurado

---

## 🎯 Acceso a la Aplicación

Una vez desplegado:

- **HTTP:** http://TU_IP_SERVIDOR/
- **HTTPS:** https://certificados.transportespuno.gob.pe/ (con SSL)
- **Admin:** https://certificados.transportespuno.gob.pe/admin/
- **Health:** https://certificados.transportespuno.gob.pe/health/

---

**Última actualización:** 2025-11-10  
**Sistema:** Ubuntu Server  
**Docker Compose:** v2 (sin guión)  
**Dominio:** certificados.transportespuno.gob.pe
