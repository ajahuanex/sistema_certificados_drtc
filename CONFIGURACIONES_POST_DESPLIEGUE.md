# 🔧 Configuraciones Post-Despliegue

## ✅ Después de ejecutar deploy-ubuntu.sh

Una vez que el despliegue esté completo, sigue estos pasos para configurar tu servidor en producción.

---

## 1️⃣ Editar Variables de Entorno para Producción

### Editar .env.production

```bash
nano .env.production
```

### Valores CRÍTICOS que debes cambiar:

```env
# 🔐 SEGURIDAD - CAMBIAR OBLIGATORIO
SECRET_KEY=genera-una-clave-unica-aqui-de-50-caracteres

# 🗄️ BASE DE DATOS
DB_PASSWORD=tu-password-postgresql-seguro

# 👤 SUPERUSUARIO
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@transportespuno.gob.pe
DJANGO_SUPERUSER_PASSWORD=tu-password-admin-seguro

# 🌐 DOMINIO (ya configurado)
ALLOWED_HOSTS=certificados.transportespuno.gob.pe,www.certificados.transportespuno.gob.pe,localhost,127.0.0.1
SITE_URL=https://certificados.transportespuno.gob.pe

# 🔒 HTTPS (activar cuando tengas SSL)
SECURE_SSL_REDIRECT=False  # Cambiar a True cuando tengas SSL
SESSION_COOKIE_SECURE=False  # Cambiar a True cuando tengas SSL
CSRF_COOKIE_SECURE=False  # Cambiar a True cuando tengas SSL
```

### Generar SECRET_KEY seguro:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Copia el resultado y pégalo en `SECRET_KEY`.

### Guardar y salir:
- Presiona `Ctrl+O` para guardar
- Presiona `Enter` para confirmar
- Presiona `Ctrl+X` para salir

### Reiniciar servicios:

```bash
docker compose -f docker-compose.prod.yml restart
```

---

## 2️⃣ Configurar Firewall

### Permitir puertos necesarios:

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

## 3️⃣ Configurar DNS

En tu proveedor de DNS (GoDaddy, Cloudflare, etc.):

```
Tipo: A
Host: certificados
Dominio: transportespuno.gob.pe
Valor: [IP_DE_TU_SERVIDOR]
TTL: 3600
```

### Verificar DNS:

```bash
# Verificar que el dominio apunta a tu servidor
nslookup certificados.transportespuno.gob.pe

# O con dig
dig certificados.transportespuno.gob.pe
```

---

## 4️⃣ Configurar SSL/HTTPS (Recomendado)

### A. Instalar Certbot

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

### B. Detener Nginx temporalmente

```bash
docker compose -f docker-compose.prod.yml stop nginx
```

### C. Obtener Certificado SSL

```bash
sudo certbot certonly --standalone -d certificados.transportespuno.gob.pe
```

Sigue las instrucciones en pantalla.

### D. Configurar Nginx para SSL

Edita la configuración de Nginx:

```bash
nano nginx.prod.conf
```

Agrega la configuración SSL (o verifica que esté):

```nginx
server {
    listen 80;
    server_name certificados.transportespuno.gob.pe;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name certificados.transportespuno.gob.pe;

    ssl_certificate /etc/letsencrypt/live/certificados.transportespuno.gob.pe/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/certificados.transportespuno.gob.pe/privkey.pem;

    # Resto de la configuración...
}
```

### E. Actualizar docker-compose.prod.yml

Asegúrate de que los certificados SSL estén montados:

```yaml
nginx:
  volumes:
    - ./nginx.prod.conf:/etc/nginx/conf.d/default.conf
    - /etc/letsencrypt:/etc/letsencrypt:ro
```

### F. Actualizar .env.production para HTTPS

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
CSRF_TRUSTED_ORIGINS=https://certificados.transportespuno.gob.pe
```

### G. Reiniciar servicios

```bash
docker compose -f docker-compose.prod.yml up -d
```

### H. Configurar Renovación Automática

```bash
# Probar renovación
sudo certbot renew --dry-run

# Certbot configurará renovación automática
```

---

## 5️⃣ Configurar Backups Automáticos

### Crear script de backup:

```bash
nano ~/backup-certificados.sh
```

Contenido:

```bash
#!/bin/bash
# Script de backup automático

BACKUP_DIR=~/backups/certificados
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR=~/dockers/sistema_certificados_drtc

# Crear directorio de backups
mkdir -p $BACKUP_DIR

# Backup de base de datos
cd $PROJECT_DIR
docker compose -f docker-compose.prod.yml exec -T db pg_dump -U certificados_user certificados_prod > $BACKUP_DIR/db_$DATE.sql

# Backup de archivos media
docker cp certificados_web_prod:/app/media $BACKUP_DIR/media_$DATE

# Comprimir
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz $BACKUP_DIR/db_$DATE.sql $BACKUP_DIR/media_$DATE

# Limpiar archivos temporales
rm -rf $BACKUP_DIR/db_$DATE.sql $BACKUP_DIR/media_$DATE

# Eliminar backups antiguos (más de 7 días)
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete

echo "Backup completado: backup_$DATE.tar.gz"
```

### Dar permisos:

```bash
chmod +x ~/backup-certificados.sh
```

### Configurar cron para backups diarios:

```bash
crontab -e
```

Agregar al final:

```cron
# Backup diario a las 2 AM
0 2 * * * ~/backup-certificados.sh >> ~/backup-certificados.log 2>&1
```

---

## 6️⃣ Configurar Monitoreo

### Script de monitoreo:

```bash
nano ~/monitor-certificados.sh
```

Contenido:

```bash
#!/bin/bash
# Script de monitoreo

PROJECT_DIR=~/dockers/sistema_certificados_drtc
cd $PROJECT_DIR

# Verificar servicios
echo "=== Estado de Servicios ==="
docker compose -f docker-compose.prod.yml ps

# Verificar health check
echo ""
echo "=== Health Check ==="
curl -f http://localhost/health/ || echo "Health check falló!"

# Verificar espacio en disco
echo ""
echo "=== Espacio en Disco ==="
df -h | grep -E "Filesystem|/$"

# Verificar uso de memoria
echo ""
echo "=== Uso de Memoria ==="
free -h
```

### Dar permisos:

```bash
chmod +x ~/monitor-certificados.sh
```

### Ejecutar manualmente:

```bash
~/monitor-certificados.sh
```

---

## 7️⃣ Crear Superusuario (si no existe)

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

Sigue las instrucciones en pantalla.

---

## 8️⃣ Verificación Final

### A. Verificar servicios:

```bash
docker compose -f docker-compose.prod.yml ps
```

Todos deben estar "Up" o "Up (healthy)".

### B. Verificar logs:

```bash
docker compose -f docker-compose.prod.yml logs --tail=50
```

No debe haber errores críticos.

### C. Verificar health check:

```bash
curl http://localhost/health/
```

Debe responder con status "healthy".

### D. Verificar acceso web:

Abre en tu navegador:
- http://TU_IP_SERVIDOR/
- http://TU_IP_SERVIDOR/admin/

O con dominio:
- https://certificados.transportespuno.gob.pe/
- https://certificados.transportespuno.gob.pe/admin/

---

## 9️⃣ Comandos Útiles del Día a Día

```bash
# Ver estado
docker compose -f docker-compose.prod.yml ps

# Ver logs
docker compose -f docker-compose.prod.yml logs -f

# Reiniciar servicios
docker compose -f docker-compose.prod.yml restart

# Backup manual
~/backup-certificados.sh

# Monitoreo manual
~/monitor-certificados.sh

# Ver uso de recursos
docker stats

# Actualizar aplicación
cd ~/dockers/sistema_certificados_drtc
git pull origin main
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d
```

---

## 🔟 Troubleshooting

### Servicios no inician:

```bash
# Ver logs detallados
docker compose -f docker-compose.prod.yml logs --tail=200

# Reconstruir desde cero
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

### Error de permisos:

```bash
# Verificar permisos de archivos
ls -la

# Dar permisos si es necesario
chmod +x deploy-ubuntu.sh
chmod +x ~/backup-certificados.sh
chmod +x ~/monitor-certificados.sh
```

### Problemas de DNS:

```bash
# Verificar DNS
nslookup certificados.transportespuno.gob.pe

# Limpiar cache DNS local
sudo systemd-resolve --flush-caches
```

### Problemas de SSL:

```bash
# Ver logs de Certbot
sudo journalctl -u certbot

# Renovar certificado manualmente
sudo certbot renew --force-renewal
```

---

## ✅ Checklist Post-Despliegue

- [ ] `.env.production` editado con valores reales
- [ ] `SECRET_KEY` generado y configurado
- [ ] Contraseñas seguras configuradas
- [ ] Firewall configurado (puertos 80, 443, 22)
- [ ] DNS configurado y propagado
- [ ] SSL/HTTPS configurado (opcional pero recomendado)
- [ ] Backups automáticos configurados
- [ ] Script de monitoreo creado
- [ ] Superusuario creado
- [ ] Servicios corriendo sin errores
- [ ] Sitio accesible desde navegador
- [ ] Health check respondiendo

---

## 📚 Documentación Adicional

- `EJECUTA_EN_UBUNTU.md` - Guía de despliegue
- `COMANDOS_UBUNTU.md` - Referencia de comandos
- `DESPLIEGUE_UBUNTU.md` - Guía completa

---

**¡Tu aplicación está lista para producción! 🎉**

**Dominio:** https://certificados.transportespuno.gob.pe/  
**Admin:** https://certificados.transportespuno.gob.pe/admin/
