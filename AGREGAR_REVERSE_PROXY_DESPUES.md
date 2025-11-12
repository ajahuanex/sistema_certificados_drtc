# Agregar Reverse Proxy con HTTPS (Para el futuro)

## Situación Actual
- Aplicación funcionando en: `http://161.132.47.92:7070`
- Sin SSL/HTTPS
- Nginx interno sirviendo archivos estáticos

## Opciones para Agregar HTTPS

### Opción 1: Nginx Reverse Proxy (Recomendado)

Instalar Nginx en el servidor host (fuera de Docker):

```bash
# Instalar nginx
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx

# Crear configuración
sudo nano /etc/nginx/sites-available/certificados
```

Contenido del archivo:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;  # O tu IP si no tienes dominio
    
    location / {
        proxy_pass http://localhost:7070;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 300s;
    }
}
```

Activar y obtener certificado SSL:

```bash
# Activar sitio
sudo ln -s /etc/nginx/sites-available/certificados /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Obtener certificado SSL (si tienes dominio)
sudo certbot --nginx -d tu-dominio.com

# Si solo tienes IP, usa certificado autofirmado:
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/nginx-selfsigned.key \
  -out /etc/ssl/certs/nginx-selfsigned.crt
```

### Opción 2: Caddy (Más fácil, SSL automático)

```bash
# Instalar Caddy
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# Crear Caddyfile
sudo nano /etc/caddy/Caddyfile
```

Contenido del Caddyfile:

```
tu-dominio.com {
    reverse_proxy localhost:7070
}

# O si solo tienes IP (sin SSL automático):
:443 {
    tls internal
    reverse_proxy localhost:7070
}
```

Reiniciar Caddy:

```bash
sudo systemctl restart caddy
```

### Opción 3: Traefik (Para múltiples servicios)

Agregar Traefik al docker-compose.prod.yml:

```yaml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
      - "--certificatesresolvers.myresolver.acme.email=tu@email.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./letsencrypt:/letsencrypt"
    networks:
      - certificados_network

  nginx:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.certificados.rule=Host(`tu-dominio.com`)"
      - "traefik.http.routers.certificados.entrypoints=websecure"
      - "traefik.http.routers.certificados.tls.certresolver=myresolver"
      - "traefik.http.services.certificados.loadbalancer.server.port=80"
```

## Actualizar Django Settings

Cuando agregues HTTPS, actualiza `.env.production`:

```bash
# Agregar estas líneas:
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Agregar tu dominio a ALLOWED_HOSTS
ALLOWED_HOSTS=161.132.47.92,tu-dominio.com

# Agregar CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS=https://tu-dominio.com
```

Reiniciar la aplicación:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production restart web
```

## Ventajas de cada opción

### Nginx
- ✅ Más control y configuración
- ✅ Muy usado y documentado
- ✅ Excelente rendimiento
- ❌ Configuración manual de SSL

### Caddy
- ✅ SSL automático con Let's Encrypt
- ✅ Configuración muy simple
- ✅ Renovación automática de certificados
- ❌ Menos conocido

### Traefik
- ✅ Perfecto para múltiples servicios
- ✅ SSL automático
- ✅ Dashboard web
- ❌ Más complejo de configurar

## Recomendación

Para tu caso, recomiendo **Caddy** si tienes un dominio, o **Nginx** si solo usarás la IP con certificado autofirmado.

## Próximos Pasos

1. Primero asegúrate de que la aplicación funciona bien con HTTP
2. Decide si vas a usar un dominio o solo IP
3. Elige el reverse proxy según tus necesidades
4. Implementa HTTPS siguiendo una de las opciones anteriores
5. Actualiza las variables de entorno de Django
6. Prueba que todo funcione correctamente
