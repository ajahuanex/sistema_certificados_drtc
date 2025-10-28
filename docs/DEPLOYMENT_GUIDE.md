# Guía Completa de Deployment

Esta guía proporciona instrucciones detalladas para desplegar el Sistema de Certificados DRTC Puno en un servidor de producción.

## Tabla de Contenidos

- [Requisitos del Servidor](#requisitos-del-servidor)
- [Preparación Inicial](#preparación-inicial)
- [Instalación Paso a Paso](#instalación-paso-a-paso)
- [Configuración de Servicios](#configuración-de-servicios)
- [Deployment Automatizado](#deployment-automatizado)
- [Verificación Post-Deployment](#verificación-post-deployment)
- [Mantenimiento](#mantenimiento)
- [Troubleshooting](#troubleshooting)

## Requisitos del Servidor

### Hardware Mínimo

| Recurso | Mínimo | Recomendado |
|---------|--------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Disco | 20 GB | 50 GB+ |
| Ancho de banda | 10 Mbps | 100 Mbps |

### Sistema Operativo

- Ubuntu 20.04 LTS o superior
- Debian 11 o superior
- CentOS 8 o superior (con ajustes)

### Software Requerido

- Python 3.10 o superior
- PostgreSQL 14 o superior
- Nginx 1.18 o superior
- Git 2.25 o superior
- Systemd

## Preparación Inicial

### 1. Actualizar el Sistema

```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

### 2. Instalar Dependencias del Sistema

```bash
# Python y herramientas
sudo apt install -y python3.10 python3.10-venv python3-pip python3-dev

# PostgreSQL
sudo apt install -y postgresql postgresql-contrib libpq-dev

# Nginx
sudo apt install -y nginx

# Git
sudo apt install -y git

# Dependencias para WeasyPrint (generación de PDFs)
sudo apt install -y \
    python3-cffi \
    python3-brotli \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info

# Herramientas adicionales
sudo apt install -y curl wget htop
```

### 3. Configurar Firewall

```bash
# Instalar UFW si no está instalado
sudo apt install -y ufw

# Configurar reglas básicas
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir SSH (¡importante antes de habilitar!)
sudo ufw allow ssh
sudo ufw allow 22/tcp

# Permitir HTTP y HTTPS
sudo ufw allow 'Nginx Full'
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Habilitar firewall
sudo ufw enable

# Verificar estado
sudo ufw status verbose
```

## Instalación Paso a Paso

### Paso 1: Configurar PostgreSQL

#### 1.1 Acceder a PostgreSQL

```bash
sudo -u postgres psql
```

#### 1.2 Crear Base de Datos y Usuario

```sql
-- Crear base de datos
CREATE DATABASE certificados_drtc;

-- Crear usuario
CREATE USER certificados_user WITH PASSWORD 'TU_PASSWORD_SEGURO_AQUI';

-- Configurar encoding y timezone
ALTER ROLE certificados_user SET client_encoding TO 'utf8';
ALTER ROLE certificados_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE certificados_user SET timezone TO 'America/Lima';

-- Otorgar privilegios
GRANT ALL PRIVILEGES ON DATABASE certificados_drtc TO certificados_user;

-- Salir
\q
```

#### 1.3 Configurar Acceso Local (Opcional)

Editar `/etc/postgresql/14/main/pg_hba.conf`:

```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

Agregar/modificar:

```
# TYPE  DATABASE              USER                ADDRESS         METHOD
local   certificados_drtc     certificados_user                   md5
host    certificados_drtc     certificados_user   127.0.0.1/32    md5
```

Reiniciar PostgreSQL:

```bash
sudo systemctl restart postgresql
```

### Paso 2: Preparar Directorio del Proyecto

#### 2.1 Crear Estructura de Directorios

```bash
# Crear directorio principal
sudo mkdir -p /var/www/certificates

# Cambiar propietario temporal para instalación
sudo chown $USER:$USER /var/www/certificates

# Crear subdirectorios
cd /var/www/certificates
mkdir -p logs media/certificates media/qr_codes backups staticfiles
```

#### 2.2 Clonar Repositorio

```bash
cd /var/www/certificates
git clone https://github.com/your-org/certificates-drtc.git .

# O si ya tienes el código, copiarlo
# scp -r /local/path/* user@server:/var/www/certificates/
```

### Paso 3: Configurar Entorno Python

#### 3.1 Crear Entorno Virtual

```bash
cd /var/www/certificates
python3.10 -m venv venv
```

#### 3.2 Activar Entorno Virtual

```bash
source venv/bin/activate
```

#### 3.3 Actualizar pip

```bash
pip install --upgrade pip setuptools wheel
```

#### 3.4 Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Nota:** Si hay errores con WeasyPrint, instala las dependencias del sistema mencionadas anteriormente.

### Paso 4: Configurar Variables de Entorno

#### 4.1 Copiar Archivo de Ejemplo

```bash
cp .env.example .env
```

#### 4.2 Generar SECRET_KEY

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

#### 4.3 Editar .env

```bash
nano .env
```

Configuración mínima:

```bash
# Django
DJANGO_ENVIRONMENT=production
SECRET_KEY=tu-secret-key-generada-aqui
DEBUG=False
ALLOWED_HOSTS=certificados.drtcpuno.gob.pe,www.certificados.drtcpuno.gob.pe

# Database
DATABASE_URL=postgresql://certificados_user:TU_PASSWORD@localhost:5432/certificados_drtc

# Media
MEDIA_ROOT=/var/www/certificates/media/
MEDIA_URL=/media/

# Static
STATIC_ROOT=/var/www/certificates/staticfiles/
STATIC_URL=/static/

# Firma Digital
SIGNATURE_SERVICE_URL=https://firma.gob.pe/api/sign
SIGNATURE_API_KEY=tu-api-key-aqui
SIGNATURE_TIMEOUT=30

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=certificados@drtcpuno.gob.pe
EMAIL_HOST_PASSWORD=tu-password-email
DEFAULT_FROM_EMAIL=certificados@drtcpuno.gob.pe

# Superuser (para creación automática)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@drtcpuno.gob.pe
DJANGO_SUPERUSER_PASSWORD=password-temporal-cambiar-despues
```

### Paso 5: Preparar la Aplicación

#### 5.1 Ejecutar Migraciones

```bash
python manage.py migrate
```

#### 5.2 Crear Superusuario

```bash
# Opción 1: Interactivo
python manage.py createsuperuser

# Opción 2: Automático (usa variables de .env)
python manage.py create_superuser_if_not_exists
```

#### 5.3 Cargar Plantilla por Defecto

```bash
python manage.py load_default_template
```

#### 5.4 Recolectar Archivos Estáticos

```bash
python manage.py collectstatic --noinput
```

#### 5.5 Verificar Configuración

```bash
python manage.py check --deploy
```

### Paso 6: Configurar Gunicorn con Systemd

#### 6.1 Copiar Archivo de Servicio

```bash
sudo cp certificates-drtc.service /etc/systemd/system/
```

#### 6.2 Editar si es Necesario

```bash
sudo nano /etc/systemd/system/certificates-drtc.service
```

Verificar rutas y configuración:

```ini
[Unit]
Description=Sistema de Certificados DRTC Puno - Gunicorn
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/certificates
Environment="PATH=/var/www/certificates/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings.production"
EnvironmentFile=/var/www/certificates/.env

ExecStart=/var/www/certificates/venv/bin/gunicorn \
    --workers 3 \
    --worker-class sync \
    --bind 127.0.0.1:8000 \
    --timeout 60 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile /var/www/certificates/logs/gunicorn-access.log \
    --error-logfile /var/www/certificates/logs/gunicorn-error.log \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance \
    config.wsgi:application

Restart=on-failure
RestartSec=5s
LimitNOFILE=4096
NoNewPrivileges=true
PrivateTmp=true
TimeoutStartSec=60
TimeoutStopSec=30
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGQUIT

[Install]
WantedBy=multi-user.target
```

#### 6.3 Configurar Permisos

```bash
# Cambiar propietario a www-data
sudo chown -R www-data:www-data /var/www/certificates

# Configurar permisos
sudo chmod -R 755 /var/www/certificates
sudo chmod -R 775 /var/www/certificates/media
sudo chmod -R 775 /var/www/certificates/logs
sudo chmod 600 /var/www/certificates/.env
```

#### 6.4 Habilitar e Iniciar Servicio

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicio (inicio automático)
sudo systemctl enable certificates-drtc

# Iniciar servicio
sudo systemctl start certificates-drtc

# Verificar estado
sudo systemctl status certificates-drtc
```

### Paso 7: Configurar Nginx

#### 7.1 Copiar Configuración

```bash
sudo cp nginx.conf.example /etc/nginx/sites-available/certificates-drtc
```

#### 7.2 Editar Configuración

```bash
sudo nano /etc/nginx/sites-available/certificates-drtc
```

Actualizar `server_name` con tu dominio:

```nginx
server_name certificados.drtcpuno.gob.pe;
```

#### 7.3 Habilitar Sitio

```bash
# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/certificates-drtc /etc/nginx/sites-enabled/

# Eliminar sitio por defecto (opcional)
sudo rm /etc/nginx/sites-enabled/default
```

#### 7.4 Probar Configuración

```bash
sudo nginx -t
```

#### 7.5 Reiniciar Nginx

```bash
sudo systemctl restart nginx
```

### Paso 8: Configurar SSL con Let's Encrypt

#### 8.1 Instalar Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

#### 8.2 Obtener Certificado

```bash
sudo certbot --nginx -d certificados.drtcpuno.gob.pe
```

Sigue las instrucciones:
- Ingresa tu email
- Acepta los términos
- Elige si quieres compartir tu email
- Elige opción 2 (redirigir HTTP a HTTPS)

#### 8.3 Verificar Renovación Automática

```bash
# Test de renovación
sudo certbot renew --dry-run

# Ver timer de renovación
sudo systemctl status certbot.timer
```

### Paso 9: Configurar Backups Automáticos

#### 9.1 Hacer Ejecutable el Script

```bash
chmod +x /var/www/certificates/backup_database.sh
```

#### 9.2 Configurar Cron

```bash
# Editar crontab
crontab -e

# Agregar línea para backup diario a las 2 AM
0 2 * * * /var/www/certificates/backup_database.sh >> /var/log/backup-certificates.log 2>&1

# Agregar línea para limpieza de logs semanalmente
0 3 * * 0 find /var/www/certificates/logs -name "*.log" -type f -mtime +30 -delete
```

## Deployment Automatizado

### Usar Script de Deployment

El proyecto incluye un script de deployment automatizado:

```bash
# Hacer ejecutable
chmod +x deploy.sh

# Ejecutar
sudo ./deploy.sh
```

El script realiza:
1. Actualización de código desde Git
2. Instalación de dependencias
3. Ejecución de migraciones
4. Recolección de archivos estáticos
5. Creación de superusuario si no existe
6. Carga de plantilla por defecto
7. Configuración de permisos
8. Reinicio de servicios
9. Verificación de estado

## Verificación Post-Deployment

### 1. Verificar Servicios

```bash
# PostgreSQL
sudo systemctl status postgresql

# Gunicorn
sudo systemctl status certificates-drtc

# Nginx
sudo systemctl status nginx
```

### 2. Verificar Conectividad

```bash
# Verificar que Gunicorn escucha en puerto 8000
sudo netstat -tlnp | grep 8000

# Verificar que Nginx escucha en puertos 80 y 443
sudo netstat -tlnp | grep nginx
```

### 3. Probar la Aplicación

```bash
# Desde el servidor
curl http://localhost

# Desde navegador
https://certificados.drtcpuno.gob.pe
https://certificados.drtcpuno.gob.pe/admin/
```

### 4. Verificar Logs

```bash
# Logs de aplicación
tail -f /var/www/certificates/logs/certificates.log

# Logs de Gunicorn
tail -f /var/www/certificates/logs/gunicorn-error.log

# Logs de Nginx
sudo tail -f /var/log/nginx/certificates-drtc-error.log

# Logs de Systemd
sudo journalctl -u certificates-drtc -f
```

### 5. Ejecutar Tests

```bash
cd /var/www/certificates
source venv/bin/activate
python manage.py test --keepdb
```

## Mantenimiento

### Actualización de la Aplicación

```bash
# Opción 1: Usar script
sudo ./deploy.sh

# Opción 2: Manual
cd /var/www/certificates
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart certificates-drtc
```

### Backup Manual

```bash
# Crear backup
./backup_database.sh

# Listar backups
./backup_database.sh --list

# Restaurar backup
./backup_database.sh --restore /path/to/backup.sql.gz
```

### Monitoreo de Recursos

```bash
# Uso de CPU y memoria
htop

# Espacio en disco
df -h

# Tamaño de base de datos
sudo -u postgres psql -d certificados_drtc -c "SELECT pg_size_pretty(pg_database_size('certificados_drtc'));"

# Tamaño de archivos media
du -sh /var/www/certificates/media/
```

### Limpieza de Logs

```bash
# Limpiar logs antiguos (más de 30 días)
find /var/www/certificates/logs -name "*.log" -type f -mtime +30 -delete

# Rotar logs manualmente
sudo logrotate -f /etc/logrotate.d/certificates-drtc
```

## Troubleshooting

### Problema: Servicio no inicia

```bash
# Ver logs detallados
sudo journalctl -u certificates-drtc -n 100 --no-pager

# Verificar configuración
cd /var/www/certificates
source venv/bin/activate
python manage.py check --deploy

# Verificar permisos
ls -la /var/www/certificates
```

### Problema: Error 502 Bad Gateway

```bash
# Verificar que Gunicorn está corriendo
sudo systemctl status certificates-drtc

# Verificar socket
sudo netstat -tlnp | grep 8000

# Reiniciar servicio
sudo systemctl restart certificates-drtc

# Ver logs
sudo journalctl -u certificates-drtc -f
```

### Problema: Error de Base de Datos

```bash
# Verificar conexión
sudo -u postgres psql -d certificados_drtc

# Verificar credenciales
cat /var/www/certificates/.env | grep DATABASE

# Ver logs de PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### Problema: Archivos Estáticos no Cargan

```bash
# Recolectar archivos
cd /var/www/certificates
source venv/bin/activate
python manage.py collectstatic --noinput

# Verificar permisos
sudo chown -R www-data:www-data /var/www/certificates/staticfiles
sudo chmod -R 755 /var/www/certificates/staticfiles

# Verificar Nginx
sudo nginx -t
sudo systemctl reload nginx
```

### Problema: Certificados SSL no Renuevan

```bash
# Verificar timer
sudo systemctl status certbot.timer

# Renovar manualmente
sudo certbot renew

# Ver logs
sudo journalctl -u certbot -n 50
```

## Checklist de Deployment

- [ ] Servidor actualizado y configurado
- [ ] PostgreSQL instalado y configurado
- [ ] Base de datos creada
- [ ] Usuario de base de datos creado
- [ ] Código clonado en `/var/www/certificates`
- [ ] Entorno virtual creado
- [ ] Dependencias instaladas
- [ ] Archivo `.env` configurado
- [ ] `SECRET_KEY` generada y única
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS` configurado
- [ ] Migraciones ejecutadas
- [ ] Superusuario creado
- [ ] Plantilla por defecto cargada
- [ ] Archivos estáticos recolectados
- [ ] Permisos configurados correctamente
- [ ] Servicio Systemd configurado
- [ ] Servicio habilitado e iniciado
- [ ] Nginx configurado
- [ ] SSL configurado con Let's Encrypt
- [ ] Firewall configurado
- [ ] Backups automáticos configurados
- [ ] Logs verificados
- [ ] Aplicación accesible desde navegador
- [ ] Panel de administración funcional
- [ ] Tests ejecutados exitosamente

## Recursos Adicionales

- [Documentación de Django Deployment](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [Guía de Gunicorn](https://docs.gunicorn.org/en/stable/deploy.html)
- [Documentación de Nginx](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/getting-started/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Soporte

Para problemas o preguntas:
- Revisar logs del sistema
- Consultar documentación del proyecto
- Contactar al equipo de desarrollo
