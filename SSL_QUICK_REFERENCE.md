# SSL/HTTPS - Referencia Rápida

## 🚀 Inicio Rápido

### Desarrollo Local
```bash
# Linux/Mac
./scripts/generate-ssl-cert.sh
docker-compose up -d
# Acceder: https://localhost:8443

# Windows
scripts\generate-ssl-cert.bat
docker-compose up -d
# Acceder: https://localhost:8443
```

### Producción (Let's Encrypt)
```bash
# Obtener certificado
sudo certbot certonly --standalone -d tu-dominio.com

# Copiar certificados
sudo cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem ssl/key.pem

# Reiniciar
docker-compose restart nginx
```

## 📋 Comandos Comunes

### Generar Certificados
```bash
# Auto-firmado (desarrollo)
./scripts/generate-ssl-cert.sh

# Let's Encrypt (producción)
sudo certbot certonly --standalone -d dominio.com
```

### Verificar Certificados
```bash
# Información completa
openssl x509 -in ssl/cert.pem -text -noout

# Solo fechas
openssl x509 -in ssl/cert.pem -noout -dates

# Verificar expiración
openssl x509 -in ssl/cert.pem -noout -checkend 0

# Verificar que clave y certificado coinciden
openssl x509 -noout -modulus -in ssl/cert.pem | openssl md5
openssl rsa -noout -modulus -in ssl/key.pem | openssl md5
```

### Renovar Certificados
```bash
# Automático (Let's Encrypt)
./scripts/renew-ssl.sh

# Manual
sudo certbot renew
sudo cp /etc/letsencrypt/live/dominio.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/dominio.com/privkey.pem ssl/key.pem
docker-compose exec nginx nginx -s reload
```

### Verificar Configuración
```bash
# Script de verificación completo
./scripts/test-ssl.sh

# Verificar nginx
docker-compose exec nginx nginx -t

# Recargar nginx sin downtime
docker-compose exec nginx nginx -s reload
```

### Test de Conectividad
```bash
# Test HTTPS básico
curl -k https://localhost:8443/health/

# Ver headers de seguridad
curl -k -I https://localhost:8443/

# Test de protocolos TLS
openssl s_client -connect localhost:8443 -tls1_2
openssl s_client -connect localhost:8443 -tls1_3

# Verificar redirección HTTP → HTTPS
curl -I http://localhost:8181/
```

## 🔧 Troubleshooting Rápido

### Certificado no encontrado
```bash
# Generar nuevo
./scripts/generate-ssl-cert.sh
```

### Certificado expirado
```bash
# Ver fecha
openssl x509 -in ssl/cert.pem -noout -dates

# Renovar
./scripts/renew-ssl.sh  # Let's Encrypt
# o
./scripts/generate-ssl-cert.sh  # Auto-firmado
```

### Nginx no inicia
```bash
# Ver error
docker-compose logs nginx

# Verificar configuración
docker-compose exec nginx nginx -t

# Verificar permisos
ls -la ssl/
chmod 644 ssl/cert.pem
chmod 600 ssl/key.pem
```

### Advertencia del navegador
```bash
# Desarrollo: Normal con certificados auto-firmados
# Chrome: escribir "thisisunsafe"
# Firefox: agregar excepción

# Producción: Usar Let's Encrypt
sudo certbot certonly --standalone -d tu-dominio.com
```

## 📁 Archivos Importantes

```
ssl/
├── cert.pem          # Certificado público
├── key.pem           # Clave privada (CONFIDENCIAL)
└── dhparam.pem       # Parámetros DH (opcional)

scripts/
├── generate-ssl-cert.sh   # Generar certificados
├── renew-ssl.sh           # Renovar Let's Encrypt
└── test-ssl.sh            # Verificar configuración

docs/
└── SSL_CONFIGURATION.md   # Documentación completa
```

## 🔐 Permisos Correctos

```bash
chmod 644 ssl/cert.pem    # Lectura pública
chmod 600 ssl/key.pem     # Solo propietario
```

## 🔄 Renovación Automática

### Configurar Cron
```bash
# Editar crontab
crontab -e

# Agregar línea (renovar cada lunes a las 3 AM)
0 3 * * 1 /ruta/completa/al/proyecto/scripts/renew-ssl.sh
```

### Verificar Cron
```bash
# Ver cron jobs
crontab -l

# Ver logs de cron
grep CRON /var/log/syslog
```

## 📊 Verificación de Seguridad

### Headers Esperados
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
```

### Verificar Headers
```bash
curl -k -I https://localhost:8443/ | grep -i "strict-transport"
curl -k -I https://localhost:8443/ | grep -i "x-frame"
curl -k -I https://localhost:8443/ | grep -i "x-content"
```

### Test SSL Labs (Producción)
```
https://www.ssllabs.com/ssltest/
Objetivo: Calificación A o A+
```

## 🎯 Checklist Rápido

### Desarrollo
- [ ] Certificados generados: `./scripts/generate-ssl-cert.sh`
- [ ] Nginx iniciado: `docker-compose up -d`
- [ ] HTTPS accesible: `https://localhost:8443`
- [ ] Redirección funciona: `curl -I http://localhost:8181/`

### Producción
- [ ] Dominio configurado y DNS apuntando al servidor
- [ ] Certbot instalado: `sudo apt-get install certbot`
- [ ] Certificado Let's Encrypt obtenido
- [ ] Certificados copiados a `ssl/`
- [ ] Renovación automática configurada (cron)
- [ ] HTTPS accesible públicamente
- [ ] Test SSL Labs: Calificación A+
- [ ] Monitoreo de expiración configurado

## 📞 Ayuda

- **Documentación completa:** `docs/SSL_CONFIGURATION.md`
- **Certificados:** `ssl/README.md`
- **Resumen de implementación:** `TASK_7_SSL_HTTPS_SUMMARY.md`

## 🔗 Enlaces Útiles

- [Let's Encrypt](https://letsencrypt.org/)
- [SSL Labs Test](https://www.ssllabs.com/ssltest/)
- [Mozilla SSL Config](https://ssl-config.mozilla.org/)
