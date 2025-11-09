# Certificados SSL/TLS

Este directorio contiene los certificados SSL/TLS para la configuración HTTPS del sistema.

## Estructura de Archivos

```
ssl/
├── README.md           # Este archivo
├── cert.pem           # Certificado SSL (público)
├── key.pem            # Clave privada SSL (privada - NO compartir)
├── dhparam.pem        # Parámetros Diffie-Hellman (opcional)
└── .gitignore         # Ignora archivos sensibles
```

## Opciones de Certificados

### Opción 1: Certificados Auto-firmados (Desarrollo/Testing)

Para generar certificados auto-firmados para pruebas locales:

```bash
# Generar certificado auto-firmado válido por 365 días
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem \
  -subj "/C=PE/ST=Lima/L=Lima/O=DRTC/CN=localhost"

# Generar parámetros Diffie-Hellman (opcional, mejora seguridad)
openssl dhparam -out ssl/dhparam.pem 2048
```

**Nota:** Los certificados auto-firmados mostrarán advertencias en los navegadores. Solo usar para desarrollo.

### Opción 2: Let's Encrypt (Producción - Recomendado)

Let's Encrypt proporciona certificados SSL gratuitos y automáticos:

```bash
# Instalar Certbot
sudo apt-get update
sudo apt-get install certbot

# Obtener certificado (asegúrate de que el puerto 80 esté accesible)
sudo certbot certonly --standalone -d tu-dominio.com -d www.tu-dominio.com

# Copiar certificados al directorio ssl/
sudo cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem ssl/key.pem

# Configurar renovación automática (los certificados expiran cada 90 días)
sudo certbot renew --dry-run
```

### Opción 3: Certificado Comercial

Si tienes un certificado SSL comercial:

1. Coloca el certificado en `ssl/cert.pem`
2. Coloca la clave privada en `ssl/key.pem`
3. Si tienes certificados intermedios, combínalos:

```bash
cat tu-certificado.crt certificado-intermedio.crt > ssl/cert.pem
```

## Configuración en Docker Compose

Los certificados se montan automáticamente en el contenedor nginx:

```yaml
nginx:
  volumes:
    - ./ssl:/etc/nginx/ssl:ro  # Montaje de solo lectura
```

## Renovación de Certificados

### Let's Encrypt (Automático)

```bash
# Renovar certificados
sudo certbot renew

# Copiar nuevos certificados
sudo cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem ssl/key.pem

# Recargar nginx sin downtime
docker-compose exec nginx nginx -s reload
```

### Script de Renovación Automática

Crear un cron job para renovación automática:

```bash
# Editar crontab
crontab -e

# Agregar línea para renovar cada semana
0 3 * * 1 /ruta/al/proyecto/scripts/renew-ssl.sh
```

## Verificación de Certificados

```bash
# Verificar certificado
openssl x509 -in ssl/cert.pem -text -noout

# Verificar fechas de expiración
openssl x509 -in ssl/cert.pem -noout -dates

# Verificar que la clave privada coincida con el certificado
openssl x509 -noout -modulus -in ssl/cert.pem | openssl md5
openssl rsa -noout -modulus -in ssl/key.pem | openssl md5
# Los hashes MD5 deben ser idénticos
```

## Seguridad

⚠️ **IMPORTANTE:**

- **NUNCA** subas `key.pem` a control de versiones
- Mantén permisos restrictivos: `chmod 600 ssl/key.pem`
- Usa certificados auto-firmados SOLO para desarrollo
- En producción, usa Let's Encrypt o certificados comerciales
- Rota certificados antes de que expiren

## Troubleshooting

### Error: "SSL certificate problem"

```bash
# Verificar que los archivos existen
ls -la ssl/

# Verificar permisos
chmod 644 ssl/cert.pem
chmod 600 ssl/key.pem
```

### Error: "nginx: [emerg] cannot load certificate"

```bash
# Verificar formato del certificado
openssl x509 -in ssl/cert.pem -text -noout

# Regenerar si es necesario
```

### Advertencia del navegador: "Certificado no confiable"

Esto es normal con certificados auto-firmados. Para desarrollo:
- Chrome: Escribe `thisisunsafe` en la página de advertencia
- Firefox: Agrega excepción de seguridad

## Referencias

- [Let's Encrypt](https://letsencrypt.org/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [SSL Labs Server Test](https://www.ssllabs.com/ssltest/)
