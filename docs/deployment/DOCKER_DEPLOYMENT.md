# 🐳 Guía de Despliegue con Docker

## 📋 Requisitos Previos

- Docker instalado (versión 20.10+)
- Docker Compose instalado (versión 2.0+)
- 2GB de RAM mínimo
- 10GB de espacio en disco

---

## 🚀 Despliegue Rápido

### 1. Clonar el Repositorio

```bash
git clone <tu-repositorio>
cd certificates-drtc
```

### 2. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus valores
nano .env
```

**Variables importantes a cambiar:**
```env
SECRET_KEY=genera-una-clave-secreta-unica
DB_PASSWORD=cambia-este-password
DJANGO_SUPERUSER_PASSWORD=cambia-este-password
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
```

### 3. Construir y Levantar Contenedores

```bash
# Construir imágenes
docker-compose build

# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 4. Verificar que Funciona

```bash
# Ver estado de contenedores
docker-compose ps

# Debería mostrar:
# certificados_db     running
# certificados_web    running
# certificados_nginx  running
```

### 5. Acceder a la Aplicación

```
http://localhost
```

**Credenciales por defecto:**
- Usuario: `admin`
- Password: El que configuraste en `.env`

---

## 📦 Estructura de Contenedores

```
┌─────────────────┐
│  Nginx (80)     │ ← Servidor web
│  Proxy reverso  │
└────────┬────────┘
         │
┌────────▼────────┐
│  Django (8000)  │ ← Aplicación
│  Gunicorn       │
└────────┬────────┘
         │
┌────────▼────────┐
│  PostgreSQL     │ ← Base de datos
│  (5432)         │
└─────────────────┘
```

---

## 🔧 Comandos Útiles

### Gestión de Contenedores

```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose stop

# Reiniciar servicios
docker-compose restart

# Ver logs
docker-compose logs -f web

# Ver logs de todos los servicios
docker-compose logs -f

# Detener y eliminar contenedores
docker-compose down

# Detener y eliminar TODO (incluyendo volúmenes)
docker-compose down -v
```

### Ejecutar Comandos Django

```bash
# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Recolectar estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Cargar plantilla por defecto
docker-compose exec web python manage.py load_default_template

# Cargar configuración QR
docker-compose exec web python manage.py load_qr_config

# Shell de Django
docker-compose exec web python manage.py shell

# Acceder al contenedor
docker-compose exec web bash
```

### Base de Datos

```bash
# Acceder a PostgreSQL
docker-compose exec db psql -U certificados_user -d certificados_db

# Backup de base de datos
docker-compose exec db pg_dump -U certificados_user certificados_db > backup.sql

# Restaurar base de datos
docker-compose exec -T db psql -U certificados_user certificados_db < backup.sql
```

---

## 🔒 Configuración de Producción

### 1. Generar SECRET_KEY Segura

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Configurar HTTPS (con Let's Encrypt)

Edita `docker-compose.yml` y agrega:

```yaml
nginx:
  volumes:
    - ./nginx-ssl.conf:/etc/nginx/nginx.conf:ro
    - ./certbot/conf:/etc/letsencrypt:ro
    - ./certbot/www:/var/www/certbot:ro
```

Luego ejecuta:

```bash
# Obtener certificado
docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  -w /var/www/certbot \
  -d tu-dominio.com \
  --email tu-email@example.com \
  --agree-tos
```

### 3. Configurar Firewall

```bash
# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Permitir SSH
sudo ufw allow 22/tcp

# Activar firewall
sudo ufw enable
```

---

## 📊 Monitoreo

### Ver Uso de Recursos

```bash
# Ver uso de CPU y memoria
docker stats

# Ver logs en tiempo real
docker-compose logs -f --tail=100

# Ver solo errores
docker-compose logs web | grep ERROR
```

### Healthcheck

```bash
# Verificar salud de contenedores
docker-compose ps

# Verificar que la app responde
curl http://localhost/consulta/
```

---

## 🔄 Actualización de la Aplicación

```bash
# 1. Hacer backup de la base de datos
docker-compose exec db pg_dump -U certificados_user certificados_db > backup_$(date +%Y%m%d).sql

# 2. Detener servicios
docker-compose down

# 3. Actualizar código
git pull origin main

# 4. Reconstruir imágenes
docker-compose build

# 5. Levantar servicios
docker-compose up -d

# 6. Ejecutar migraciones
docker-compose exec web python manage.py migrate

# 7. Recolectar estáticos
docker-compose exec web python manage.py collectstatic --noinput

# 8. Verificar logs
docker-compose logs -f
```

---

## 🐛 Solución de Problemas

### Problema: Contenedor web no inicia

```bash
# Ver logs detallados
docker-compose logs web

# Verificar que la base de datos está lista
docker-compose exec db pg_isready -U certificados_user

# Reiniciar servicios
docker-compose restart
```

### Problema: Error de conexión a base de datos

```bash
# Verificar que el contenedor db está corriendo
docker-compose ps db

# Verificar variables de entorno
docker-compose exec web env | grep DB_

# Reiniciar base de datos
docker-compose restart db
```

### Problema: Archivos estáticos no se cargan

```bash
# Recolectar estáticos nuevamente
docker-compose exec web python manage.py collectstatic --noinput

# Verificar permisos
docker-compose exec web ls -la /app/staticfiles/

# Reiniciar nginx
docker-compose restart nginx
```

### Problema: Permisos de archivos

```bash
# Cambiar propietario de archivos
sudo chown -R 1000:1000 media/ staticfiles/ logs/

# Dar permisos de escritura
chmod -R 755 media/ staticfiles/ logs/
```

---

## 📁 Volúmenes y Persistencia

### Ubicación de Datos

```
./media/          → Archivos subidos (PDFs, QR codes)
./staticfiles/    → Archivos estáticos (CSS, JS, imágenes)
./logs/           → Logs de la aplicación
postgres_data/    → Datos de PostgreSQL (volumen Docker)
```

### Backup Completo

```bash
# Crear directorio de backup
mkdir -p backups/$(date +%Y%m%d)

# Backup de base de datos
docker-compose exec db pg_dump -U certificados_user certificados_db > \
  backups/$(date +%Y%m%d)/database.sql

# Backup de archivos media
tar -czf backups/$(date +%Y%m%d)/media.tar.gz media/

# Backup de archivos estáticos
tar -czf backups/$(date +%Y%m%d)/staticfiles.tar.gz staticfiles/
```

---

## 🚀 Despliegue en Servidor de Producción

### Opción 1: VPS (DigitalOcean, Linode, etc.)

```bash
# 1. Conectar al servidor
ssh root@tu-servidor.com

# 2. Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 3. Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Clonar repositorio
git clone <tu-repositorio> /var/www/certificates
cd /var/www/certificates

# 5. Configurar .env
cp .env.example .env
nano .env

# 6. Levantar servicios
docker-compose up -d

# 7. Configurar dominio y SSL
# (Ver sección de HTTPS arriba)
```

### Opción 2: AWS ECS / Azure Container Instances

Ver documentación específica de cada proveedor.

---

## 📈 Optimización de Producción

### 1. Aumentar Workers de Gunicorn

Edita `docker-compose.yml`:

```yaml
web:
  command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 5 --timeout 120
```

**Fórmula:** `workers = (2 x CPU cores) + 1`

### 2. Configurar Caché con Redis

Agrega a `docker-compose.yml`:

```yaml
redis:
  image: redis:7-alpine
  container_name: certificados_redis
  restart: unless-stopped
  networks:
    - certificados_network
```

### 3. Logs Rotativos

Agrega a `docker-compose.yml`:

```yaml
web:
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```

---

## ✅ Checklist de Despliegue

- [ ] Variables de entorno configuradas
- [ ] SECRET_KEY generada y segura
- [ ] Passwords cambiados
- [ ] ALLOWED_HOSTS configurado
- [ ] Base de datos funcionando
- [ ] Migraciones ejecutadas
- [ ] Superusuario creado
- [ ] Archivos estáticos recolectados
- [ ] Plantilla por defecto cargada
- [ ] Configuración QR cargada
- [ ] Nginx funcionando
- [ ] HTTPS configurado (producción)
- [ ] Firewall configurado
- [ ] Backups configurados
- [ ] Monitoreo configurado

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker-compose logs -f`
2. Verifica el estado: `docker-compose ps`
3. Consulta esta documentación
4. Revisa los archivos de configuración

---

**¡Tu aplicación está lista para producción!** 🎉

Para más información, consulta:
- `README.md` - Documentación general
- `docs/DEPLOYMENT_GUIDE.md` - Guía de despliegue tradicional
- `docs/ADMIN_GUIDE.md` - Guía de administración
