# Configuración SSL/HTTPS

Esta guía explica cómo configurar SSL/HTTPS para el sistema de certificados DRTC en producción.

## Tabla de Contenidos

- [Visión General](#visión-general)
- [Opciones de Certificados](#opciones-de-certificados)
- [Configuración Rápida](#configuración-rápida)
- [Configuración Detallada](#configuración-detallada)
- [Renovación de Certificados](#renovación-de-certificados)
- [Seguridad](#seguridad)
- [Troubleshooting](#troubleshooting)

## Visión General

El sistema está configurado para usar HTTPS con las siguientes características:

- ✅ Redirección automática HTTP → HTTPS
- ✅ TLS 1.2 y 1.3 únicamente
- ✅ Cifrados modernos y seguros
- ✅ HSTS (HTTP Strict Transport Security)
- ✅ Headers de seguridad completos
- ✅ OCSP Stapling
- ✅ Optimización de sesiones SSL

## Opciones de Certificados

### 1. Certificados Auto-firmados (Desarrollo)

**Ventajas:**
- Rápido y fácil de configurar
- Gratis
- Ideal para desarrollo local

**Desventajas:**
- Advertencias en navegadores
- No válido para producción
- No confiable públicamente

### 2. Let's Encrypt (Producción - Recomendado)

**Ventajas:**
- Gratis y automático
- Confiable públicamente
- Renovación automática
- Ideal para producción

**Desventajas:**
- Requiere dominio público
- Requiere puerto 80 accesible

### 3. Certificado Comercial (Producción)

**Ventajas:**
- Máxima confiabilidad
- Soporte técnico
- Garantías

**Desventajas:**
- Costo anual
- Proceso de validación manual

## Configuración Rápida

### Opción A: Certificados Auto-firmados (Desarrollo)

```bash
# Linux/Mac
./scripts/generate-ssl-cert.sh

# Windows
scripts\generate-ssl-cert.bat

# Reiniciar nginx
docker-compose restart nginx
```

### Opción B: Let's Encrypt (Producción)

```bash
# 1. Instalar Certbot
sudo apt-get update
sudo apt-get install certbot

# 2. Detener nginx temporalmente
docker-compose stop nginx

# 3. Obtener certificado
sudo certbot certonly --standalone \
  -d tu-dominio.com \
  -d www.tu-dominio.com \
  --email tu-email@example.com \
  --agree-tos

# 4. Copiar certificados
sudo cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem ssl/key.pem
sudo chown $(whoami):$(whoami) ssl/*.pem
chmod 644 ssl/cert.pem
chmod 600 ssl/key.pem

# 5. Iniciar nginx
docker-compose start nginx
```

## Configuración Detallada

### Estructura de Archivos SSL

```
ssl/
├── cert.pem          # Certificado público (compartible)
├── key.pem           # Clave privada (CONFIDENCIAL)
├── dhparam.pem       # Parámetros DH (opcional)
└── README.md         # Documentación
```

### Configuración en Nginx

El archivo `nginx.prod.conf` ya está configurado con:

```nginx
server {
    listen 443 ssl http2;
    
    # Certificados
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # Protocolos modernos
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # Cifrados seguros
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256...;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Headers de seguridad
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    # ... más headers
}
```

### Configuración en Django

Agregar a `.env.production`:

```bash
# SSL/HTTPS
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

## Renovación de Certificados

### Let's Encrypt - Renovación Automática

Los certificados de Let's Encrypt expiran cada 90 días. Configurar renovación automática:

#### Método 1: Cron Job

```bash
# Editar crontab
crontab -e

# Agregar línea para renovar semanalmente (lunes a las 3 AM)
0 3 * * 1 /ruta/completa/al/proyecto/scripts/renew-ssl.sh >> /var/log/ssl-renewal.log 2>&1
```

#### Método 2: Systemd Timer

```bash
# Crear archivo /etc/systemd/system/certbot-renewal.service
[Unit]
Description=Renovación de certificados SSL
After=network.target

[Service]
Type=oneshot
ExecStart=/ruta/completa/al/proyecto/scripts/renew-ssl.sh

# Crear archivo /etc/systemd/system/certbot-renewal.timer
[Unit]
Description=Timer para renovación de certificados SSL

[Timer]
OnCalendar=weekly
Persistent=true

[Install]
WantedBy=timers.target

# Habilitar timer
sudo systemctl enable certbot-renewal.timer
sudo systemctl start certbot-renewal.timer
```

#### Método 3: Manual

```bash
# Ejecutar script de renovación
./scripts/renew-ssl.sh

# O renovar manualmente
sudo certbot renew
sudo cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem ssl/key.pem
docker-compose exec nginx nginx -s reload
```

### Verificar Renovación Automática

```bash
# Probar renovación (dry-run)
sudo certbot renew --dry-run

# Ver estado de certificados
sudo certbot certificates

# Ver próxima ejecución del cron
crontab -l
```

## Seguridad

### Mejores Prácticas

1. **Proteger Clave Privada**
   ```bash
   chmod 600 ssl/key.pem
   chown root:root ssl/key.pem  # En producción
   ```

2. **No Subir a Git**
   - El archivo `ssl/.gitignore` ya está configurado
   - Verificar: `git status ssl/`

3. **Usar Certificados Válidos en Producción**
   - NUNCA usar certificados auto-firmados en producción
   - Preferir Let's Encrypt o certificados comerciales

4. **Monitorear Expiración**
   ```bash
   # Ver fecha de expiración
   openssl x509 -in ssl/cert.pem -noout -dates
   
   # Configurar alertas 30 días antes
   ```

5. **Backup de Certificados**
   ```bash
   # Incluir en backup regular
   tar -czf backup-ssl-$(date +%Y%m%d).tar.gz ssl/
   ```

### Headers de Seguridad Implementados

| Header | Valor | Propósito |
|--------|-------|-----------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | Forzar HTTPS por 1 año |
| `X-Frame-Options` | `DENY` | Prevenir clickjacking |
| `X-Content-Type-Options` | `nosniff` | Prevenir MIME sniffing |
| `X-XSS-Protection` | `1; mode=block` | Protección XSS |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Control de referrer |
| `Content-Security-Policy` | Configurado | Prevenir XSS y ataques |
| `Permissions-Policy` | Configurado | Control de permisos |

### Verificar Configuración SSL

```bash
# Test local
curl -I https://localhost:8443

# Test de seguridad SSL Labs (producción)
# Visitar: https://www.ssllabs.com/ssltest/
# Objetivo: Calificación A o A+

# Test con OpenSSL
openssl s_client -connect localhost:8443 -tls1_2
openssl s_client -connect localhost:8443 -tls1_3

# Verificar headers de seguridad
curl -I https://localhost:8443 | grep -i "strict-transport"
```

## Troubleshooting

### Error: "SSL certificate problem: self signed certificate"

**Causa:** Usando certificado auto-firmado

**Solución para desarrollo:**
```bash
# Curl: ignorar verificación SSL
curl -k https://localhost:8443

# Navegador Chrome: escribir "thisisunsafe" en la página de advertencia
# Navegador Firefox: agregar excepción de seguridad
```

**Solución para producción:**
```bash
# Usar Let's Encrypt o certificado comercial
./scripts/generate-ssl-cert.sh  # Solo para desarrollo
```

### Error: "nginx: [emerg] cannot load certificate"

**Causa:** Certificados no encontrados o formato incorrecto

**Solución:**
```bash
# Verificar que existen
ls -la ssl/

# Verificar formato
openssl x509 -in ssl/cert.pem -text -noout

# Regenerar si es necesario
./scripts/generate-ssl-cert.sh
```

### Error: "SSL handshake failed"

**Causa:** Configuración SSL incorrecta

**Solución:**
```bash
# Ver logs de nginx
docker-compose logs nginx

# Verificar configuración
docker-compose exec nginx nginx -t

# Verificar permisos
ls -la ssl/
chmod 644 ssl/cert.pem
chmod 600 ssl/key.pem
```

### Error: "Certificate has expired"

**Causa:** Certificado expirado

**Solución:**
```bash
# Verificar fecha de expiración
openssl x509 -in ssl/cert.pem -noout -dates

# Renovar certificado
./scripts/renew-ssl.sh

# O regenerar auto-firmado
./scripts/generate-ssl-cert.sh
```

### Advertencia: "NET::ERR_CERT_AUTHORITY_INVALID"

**Causa:** Certificado auto-firmado o no confiable

**Solución para desarrollo:**
- Aceptar riesgo en navegador
- Chrome: escribir "thisisunsafe"
- Firefox: agregar excepción

**Solución para producción:**
- Usar Let's Encrypt o certificado comercial

### Puerto 443 ya en uso

**Causa:** Otro servicio usando puerto 443

**Solución:**
```bash
# Ver qué está usando el puerto
sudo netstat -tlnp | grep :443
# o
sudo lsof -i :443

# Detener servicio conflictivo o cambiar puerto en docker-compose.prod.yml
# Cambiar "8443:443" a otro puerto como "8444:443"
```

## Comandos Útiles

```bash
# Generar certificado auto-firmado
./scripts/generate-ssl-cert.sh

# Renovar Let's Encrypt
./scripts/renew-ssl.sh

# Ver información del certificado
openssl x509 -in ssl/cert.pem -text -noout

# Ver fecha de expiración
openssl x509 -in ssl/cert.pem -noout -dates

# Verificar que clave y certificado coinciden
openssl x509 -noout -modulus -in ssl/cert.pem | openssl md5
openssl rsa -noout -modulus -in ssl/key.pem | openssl md5

# Recargar nginx sin downtime
docker-compose exec nginx nginx -s reload

# Test de conexión SSL
openssl s_client -connect localhost:8443 -showcerts

# Ver cifrados soportados
nmap --script ssl-enum-ciphers -p 8443 localhost
```

## Referencias

- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [SSL Labs Server Test](https://www.ssllabs.com/ssltest/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [OWASP TLS Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html)
- [Nginx SSL Module](http://nginx.org/en/docs/http/ngx_http_ssl_module.html)

## Checklist de Producción

- [ ] Certificados SSL válidos instalados (Let's Encrypt o comercial)
- [ ] Redirección HTTP → HTTPS funcionando
- [ ] HSTS habilitado
- [ ] Headers de seguridad configurados
- [ ] Renovación automática configurada (cron/systemd)
- [ ] Backup de certificados configurado
- [ ] Monitoreo de expiración configurado
- [ ] Test SSL Labs con calificación A o superior
- [ ] Logs de nginx monitoreados
- [ ] Documentación actualizada con dominio real
