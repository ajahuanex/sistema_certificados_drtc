# 🚀 Comandos Rápidos - Despliegue Remoto

## 📋 Índice Rápido

1. [Subir a GitHub](#subir-a-github)
2. [Conectar al Servidor](#conectar-al-servidor)
3. [Primera Instalación](#primera-instalación)
4. [Actualizar Aplicación](#actualizar-aplicación)
5. [Comandos de Gestión](#comandos-de-gestión)
6. [Troubleshooting](#troubleshooting)

---

## 1. Subir a GitHub

### Desde Windows (Local)

```cmd
REM Opción A: Script automatizado
SUBIR_A_GITHUB_AHORA.bat

REM Opción B: Comandos manuales
git add .
git commit -m "feat: Actualización del sistema"
git push origin main
```

---

## 2. Conectar al Servidor

```bash
# Conectar por SSH
ssh usuario@IP_DEL_SERVIDOR

# O con archivo de clave
ssh -i ~/.ssh/mi_clave.pem usuario@IP_DEL_SERVIDOR
```

---

## 3. Primera Instalación

### 3.1 Instalar Docker

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker --version
docker-compose --version

# IMPORTANTE: Cerrar sesión y volver a conectar
exit
ssh usuario@IP_DEL_SERVIDOR
```

### 3.2 Clonar Repositorio

```bash
# Clonar desde GitHub
git clone https://github.com/TU_USUARIO/TU_REPO.git

# Entrar al directorio
cd TU_REPO
```

### 3.3 Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.production.example .env.production

# Editar variables
nano .env.production
```

**Variables críticas a configurar:**

```bash
SECRET_KEY=genera-una-clave-secreta-larga-y-aleatoria
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com,IP_DEL_SERVIDOR

POSTGRES_PASSWORD=password-seguro-postgres
REDIS_PASSWORD=password-seguro-redis

DOMAIN=tu-dominio.com
SSL_EMAIL=tu-email@example.com
```

**Generar SECRET_KEY:**

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3.4 Dar Permisos a Scripts

```bash
chmod +x deploy-ubuntu.sh
chmod +x scripts/*.sh
chmod +x *.sh
```

### 3.5 Desplegar

```bash
./deploy-ubuntu.sh
```

---

## 4. Actualizar Aplicación

### Actualización Completa

```bash
# Conectar al servidor
ssh usuario@IP_DEL_SERVIDOR

# Ir al directorio del proyecto
cd TU_REPO

# Actualizar código desde GitHub
git pull origin main

# Reconstruir y reiniciar
docker-compose build
docker-compose up -d

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Recolectar estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Reiniciar servicios
docker-compose restart
```

### Actualización Rápida (sin rebuild)

```bash
# Actualizar código
git pull origin main

# Reiniciar solo el servicio web
docker-compose restart web
```

---

## 5. Comandos de Gestión

### Ver Estado de Servicios

```bash
# Ver todos los contenedores
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f postgres
docker-compose logs -f redis

# Ver últimas 50 líneas
docker-compose logs --tail=50
```

### Gestión de Contenedores

```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Reiniciar servicios
docker-compose restart

# Reiniciar un servicio específico
docker-compose restart web

# Reconstruir imágenes
docker-compose build --no-cache

# Ver uso de recursos
docker stats
```

### Ejecutar Comandos Django

```bash
# Ejecutar cualquier comando de Django
docker-compose exec web python manage.py [comando]

# Ejemplos:
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell

# Cambiar contraseña de admin
docker-compose exec web python manage.py changepassword admin

# Generar datos de prueba
docker-compose exec web python manage.py generate_sample_data
```

### Base de Datos

```bash
# Acceder a PostgreSQL
docker-compose exec postgres psql -U certificados_user -d certificados_db

# Backup de base de datos
docker-compose exec postgres pg_dump -U certificados_user certificados_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar base de datos
docker-compose exec -T postgres psql -U certificados_user certificados_db < backup_20250117_120000.sql

# Ver tamaño de la base de datos
docker-compose exec postgres psql -U certificados_user -d certificados_db -c "SELECT pg_size_pretty(pg_database_size('certificados_db'));"
```

### Redis

```bash
# Acceder a Redis CLI
docker-compose exec redis redis-cli

# Verificar conexión
docker-compose exec redis redis-cli ping

# Ver estadísticas
docker-compose exec redis redis-cli INFO

# Limpiar caché
docker-compose exec redis redis-cli FLUSHALL
```

### Nginx

```bash
# Verificar configuración
docker-compose exec nginx nginx -t

# Recargar configuración
docker-compose exec nginx nginx -s reload

# Ver logs de acceso
docker-compose exec nginx tail -f /var/log/nginx/access.log

# Ver logs de error
docker-compose exec nginx tail -f /var/log/nginx/error.log
```

---

## 6. Troubleshooting

### Problema: Contenedores no inician

```bash
# Ver logs detallados
docker-compose logs

# Ver logs de un servicio específico
docker-compose logs web

# Reiniciar todo
docker-compose down
docker-compose up -d

# Reconstruir desde cero
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Problema: Error de base de datos

```bash
# Ver logs de PostgreSQL
docker-compose logs postgres

# Verificar que PostgreSQL esté corriendo
docker-compose ps postgres

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Verificar conexión
docker-compose exec web python manage.py check --database default
```

### Problema: Archivos estáticos no cargan

```bash
# Recolectar archivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Verificar permisos
docker-compose exec web ls -la /app/staticfiles

# Reiniciar nginx
docker-compose restart nginx

# Ver logs de nginx
docker-compose logs nginx
```

### Problema: Puerto ocupado

```bash
# Ver qué está usando el puerto 80
sudo lsof -i :80

# Ver qué está usando el puerto 443
sudo lsof -i :443

# Detener Apache si está instalado
sudo systemctl stop apache2
sudo systemctl disable apache2

# Detener nginx si está instalado fuera de Docker
sudo systemctl stop nginx
sudo systemctl disable nginx
```

### Problema: Sin espacio en disco

```bash
# Ver uso de disco
df -h

# Limpiar imágenes Docker no usadas
docker system prune -a

# Limpiar volúmenes no usados
docker volume prune

# Ver uso de Docker
docker system df
```

### Problema: Memoria insuficiente

```bash
# Ver uso de memoria
free -h

# Ver uso por contenedor
docker stats

# Reiniciar contenedores para liberar memoria
docker-compose restart
```

---

## 📊 Comandos de Monitoreo

### Ver Recursos en Tiempo Real

```bash
# Uso de CPU y memoria por contenedor
docker stats

# Uso de disco
df -h

# Uso de memoria del sistema
free -h

# Procesos del sistema
top
```

### Health Checks

```bash
# Verificar salud de la aplicación
curl http://localhost/health/

# Verificar base de datos
docker-compose exec web python manage.py check --database default

# Verificar Redis
docker-compose exec redis redis-cli ping

# Verificar nginx
docker-compose exec nginx nginx -t
```

---

## 🔐 Seguridad

### Cambiar Contraseñas

```bash
# Cambiar contraseña de admin Django
docker-compose exec web python manage.py changepassword admin

# Cambiar contraseña de PostgreSQL
docker-compose exec postgres psql -U postgres -c "ALTER USER certificados_user WITH PASSWORD 'nueva_password';"

# Actualizar .env.production con la nueva password
nano .env.production
```

### Configurar SSL

```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx -y

# Generar certificado
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Verificar renovación automática
sudo certbot renew --dry-run
```

---

## 📦 Backups

### Backup Manual

```bash
# Backup de base de datos
docker-compose exec postgres pg_dump -U certificados_user certificados_db > backup_db_$(date +%Y%m%d).sql

# Backup de archivos media
tar -czf backup_media_$(date +%Y%m%d).tar.gz media/

# Backup completo
./backup_database.sh
```

### Restaurar Backup

```bash
# Restaurar base de datos
docker-compose exec -T postgres psql -U certificados_user certificados_db < backup_db_20250117.sql

# Restaurar archivos media
tar -xzf backup_media_20250117.tar.gz
```

---

## 🔄 Rollback

### Volver a Versión Anterior

```bash
# Ver commits recientes
git log --oneline -10

# Volver a un commit específico
git checkout [COMMIT_HASH]

# Reconstruir y reiniciar
docker-compose build
docker-compose up -d

# Ejecutar migraciones si es necesario
docker-compose exec web python manage.py migrate
```

---

## 📝 Logs

### Ver Logs

```bash
# Todos los logs
docker-compose logs

# Logs en tiempo real
docker-compose logs -f

# Últimas 100 líneas
docker-compose logs --tail=100

# Logs de un servicio
docker-compose logs -f web

# Logs de Django
docker-compose exec web tail -f logs/django.log
```

---

## 🎯 Checklist de Despliegue

```bash
# 1. Subir código a GitHub
git push origin main

# 2. Conectar al servidor
ssh usuario@IP_DEL_SERVIDOR

# 3. Actualizar código
cd TU_REPO
git pull origin main

# 4. Reconstruir y reiniciar
docker-compose build
docker-compose up -d

# 5. Ejecutar migraciones
docker-compose exec web python manage.py migrate

# 6. Recolectar estáticos
docker-compose exec web python manage.py collectstatic --noinput

# 7. Verificar estado
docker-compose ps
curl http://localhost/health/

# 8. Ver logs
docker-compose logs --tail=50
```

---

## 📚 Documentación Relacionada

- **GUIA_DESPLIEGUE_REMOTO.md** - Guía completa paso a paso
- **GUIA_DESPLIEGUE_PRODUCCION_2025.md** - Guía de producción detallada
- **docs/PRODUCTION_DEPLOYMENT.md** - Documentación técnica

---

**¡Guarda este archivo como referencia rápida!** 📌
