# 🚀 Guía Completa de Despliegue a Producción

## 📋 Prerrequisitos del Servidor

### Servidor Mínimo Requerido
- **CPU**: 2 cores (4 cores recomendado)
- **RAM**: 4GB mínimo, 8GB recomendado
- **Disco**: 50GB SSD (100GB recomendado)
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **Red**: Conexión estable a internet

### Software Requerido

#### 1. Docker y Docker Compose
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker --version
docker-compose --version
```

#### 2. Git
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y git

# CentOS/RHEL
sudo yum install -y git

# Verificar instalación
git --version
```

#### 3. Nginx (opcional, si no usas el contenedor)
```bash
# Ubuntu/Debian
sudo apt install -y nginx

# CentOS/RHEL
sudo yum install -y nginx
```

## 🔧 Configuración Inicial

### 1. Preparar Directorio de Aplicación
```bash
# Crear directorio de aplicación
sudo mkdir -p /app
sudo chown $USER:$USER /app

# Cambiar al directorio
cd /app
```

### 2. Clonar Repositorio desde GitHub
```bash
# Clonar el repositorio
git clone https://github.com/ajahuanex/sistema_certificados_drtc.git .

# Verificar que se clonó correctamente
ls -la
```

### 3. Configurar Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp .env.production.example .env.production

# Editar configuración (usar nano, vim, o tu editor preferido)
nano .env.production
```

#### Variables Críticas a Configurar:
```bash
# CAMBIAR OBLIGATORIAMENTE:
SECRET_KEY=tu_secret_key_super_seguro_de_50_caracteres_minimo
DB_PASSWORD=password_super_seguro_para_bd
EMAIL_HOST_PASSWORD=tu_app_password_de_gmail
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# Configurar según tu dominio:
SITE_URL=https://tu-dominio.com
CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
```

### 4. Crear Directorios Necesarios
```bash
# Crear directorios para volúmenes
mkdir -p media staticfiles logs backups ssl

# Establecer permisos
chmod 755 media staticfiles logs backups
chmod 700 ssl  # Solo para certificados SSL
```

## 🚀 Despliegue Inicial

### 1. Construir y Levantar Servicios
```bash
# Construir imágenes
docker-compose -f docker-compose.prod.yml build

# Levantar servicios en segundo plano
docker-compose -f docker-compose.prod.yml up -d

# Verificar que todos los servicios están corriendo
docker-compose -f docker-compose.prod.yml ps
```

### 2. Configurar Base de Datos
```bash
# Ejecutar migraciones
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Recopilar archivos estáticos
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Crear superusuario
docker-compose -f docker-compose.prod.yml exec web python manage.py create_superuser_if_not_exists

# Cargar plantilla por defecto
docker-compose -f docker-compose.prod.yml exec web python manage.py load_default_template
```

### 3. Verificar Funcionamiento
```bash
# Verificar logs
docker-compose -f docker-compose.prod.yml logs web

# Probar endpoint de salud
curl -f http://localhost/health/

# Verificar que la aplicación responde
curl -I http://localhost/
```

## 🔒 Configuración SSL/HTTPS

### Opción 1: Let's Encrypt (Recomendado)
```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado
sudo certbot certonly --standalone -d tu-dominio.com -d www.tu-dominio.com

# Copiar certificados al directorio SSL
sudo cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem /app/ssl/cert.pem
sudo cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem /app/ssl/key.pem
sudo chown $USER:$USER /app/ssl/*.pem

# Configurar renovación automática
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### Opción 2: Certificado Propio
```bash
# Generar certificado autofirmado (solo para pruebas)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -subj "/C=PE/ST=Puno/L=Puno/O=DRTC/CN=tu-dominio.com"
```

## 🔄 Sistema de Actualizaciones Automáticas

### Método 1: Script Manual (Recomendado)
```bash
# Hacer ejecutable el script
chmod +x update-production.sh

# Ejecutar actualización
./update-production.sh
```

### Método 2: Cron Job Automático
```bash
# Editar crontab
crontab -e

# Agregar línea para actualización diaria a las 3 AM
0 3 * * * cd /app && ./update-production.sh >> logs/cron-update.log 2>&1
```

### Método 3: Webhook de GitHub
```bash
# Instalar Flask para webhook (opcional)
pip3 install flask

# Crear archivo webhook_server.py (ver ejemplo en documentación)
# Ejecutar servidor webhook
python3 webhook_server.py &

# Configurar webhook en GitHub:
# URL: http://tu-servidor:9000/webhook
# Content type: application/json
# Secret: tu_webhook_secret
```

## 📊 Monitoreo y Mantenimiento

### 1. Verificar Estado de Servicios
```bash
# Ver estado de contenedores
docker-compose -f docker-compose.prod.yml ps

# Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f web

# Ver logs específicos
docker-compose -f docker-compose.prod.yml logs --tail=100 web
```

### 2. Backup Automático
```bash
# Crear script de backup
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/app/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup de base de datos
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U certificados_user certificados_prod > "$BACKUP_DIR/db_backup_$DATE.sql"

# Backup de archivos media
tar -czf "$BACKUP_DIR/media_backup_$DATE.tar.gz" -C /app media/

# Limpiar backups antiguos (mantener últimos 7 días)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "✅ Backup completado: $DATE"
EOF

chmod +x backup.sh

# Programar backup diario
echo "0 2 * * * cd /app && ./backup.sh" | crontab -
```

### 3. Monitoreo de Recursos
```bash
# Ver uso de recursos de contenedores
docker stats

# Ver espacio en disco
df -h

# Ver logs del sistema
journalctl -u docker.service -f
```

## 🆘 Solución de Problemas

### Problemas Comunes

#### 1. Aplicación no inicia
```bash
# Ver logs detallados
docker-compose -f docker-compose.prod.yml logs web

# Verificar configuración
docker-compose -f docker-compose.prod.yml config

# Reconstruir imagen
docker-compose -f docker-compose.prod.yml build --no-cache web
```

#### 2. Base de datos no conecta
```bash
# Verificar estado de PostgreSQL
docker-compose -f docker-compose.prod.yml exec db pg_isready -U certificados_user

# Conectar manualmente a la BD
docker-compose -f docker-compose.prod.yml exec db psql -U certificados_user -d certificados_prod

# Ver logs de la base de datos
docker-compose -f docker-compose.prod.yml logs db
```

#### 3. Archivos estáticos no cargan
```bash
# Recopilar archivos estáticos
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Verificar permisos
ls -la staticfiles/

# Verificar configuración de Nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

#### 4. SSL/HTTPS no funciona
```bash
# Verificar certificados
openssl x509 -in ssl/cert.pem -text -noout

# Verificar configuración de Nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Recargar configuración de Nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Rollback de Emergencia
```bash
#!/bin/bash
# rollback.sh

echo "🔄 Iniciando rollback de emergencia..."

# Volver al commit anterior
git reset --hard HEAD~1

# Restaurar backup de BD si es necesario
# docker-compose -f docker-compose.prod.yml exec -T db psql -U certificados_user -d certificados_prod < backups/backup_YYYYMMDD_HHMMSS.sql

# Reiniciar servicios
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

echo "✅ Rollback completado"
```

## ✅ Checklist de Verificación Post-Despliegue

### Funcionalidad Básica
- [ ] Aplicación accesible vía HTTP/HTTPS
- [ ] Panel de administración funciona (`/admin/`)
- [ ] Página de inicio carga correctamente
- [ ] Health check responde (`/health/`)

### Funcionalidades Específicas
- [ ] Importación de Excel funciona
- [ ] Generación de certificados funciona
- [ ] Editor de plantillas funciona
- [ ] Consulta pública funciona
- [ ] Dashboard de estadísticas funciona

### Seguridad
- [ ] HTTPS configurado y funcionando
- [ ] Redirección HTTP → HTTPS activa
- [ ] Headers de seguridad configurados
- [ ] Rate limiting funcionando

### Rendimiento
- [ ] Archivos estáticos se sirven correctamente
- [ ] Compresión gzip activa
- [ ] Cache de Redis funcionando
- [ ] Tiempos de respuesta aceptables

### Monitoreo
- [ ] Logs configurados y accesibles
- [ ] Backups automáticos funcionando
- [ ] Health checks respondiendo
- [ ] Métricas de sistema disponibles

## 📞 Contacto y Soporte

Para problemas en producción:

1. **Revisar logs**: `docker-compose -f docker-compose.prod.yml logs -f web`
2. **Verificar estado**: `docker-compose -f docker-compose.prod.yml ps`
3. **Consultar esta documentación**
4. **Contactar soporte técnico** con información detallada del error

### Información Útil para Soporte
- Versión del sistema: `git rev-parse HEAD`
- Estado de contenedores: `docker-compose ps`
- Logs recientes: `tail -100 logs/django.log`
- Configuración: `docker-compose config`

---

## 🎉 ¡Felicidades!

Si has llegado hasta aquí y todos los checks están ✅, tu sistema de certificados DRTC está **listo para producción** con:

- ✅ **Dockerización completa**
- ✅ **Actualizaciones automáticas desde GitHub**
- ✅ **Backups automáticos**
- ✅ **Monitoreo y logs**
- ✅ **Seguridad SSL/HTTPS**
- ✅ **Alta disponibilidad**

**¡Tu sistema está listo para servir certificados a la comunidad!** 🚀