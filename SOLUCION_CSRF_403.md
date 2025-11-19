# 🔧 SOLUCIÓN ERROR 403 CSRF

## Problema
Error "Prohibido (403) - La verificación CSRF ha fallado" al acceder al admin a través del dominio HTTPS.

## Verificación Realizada

✅ Las configuraciones de Django están correctas:
```python
ALLOWED_HOSTS = ['161.132.47.92', 'localhost', '127.0.0.1', 'certificados.transportespuno.gob.pe', 'www.certificados.transportespuno.gob.pe']

CSRF_TRUSTED_ORIGINS = ['http://161.132.47.92', 'http://localhost', 'https://certificados.transportespuno.gob.pe', 'https://www.certificados.transportespuno.gob.pe']
```

## Causas Posibles

### 1. Cookies Antiguas en el Navegador
El navegador tiene cookies con tokens CSRF antiguos que ya no son válidos.

### 2. Nginx Proxy Manager - Headers Faltantes
Nginx Proxy Manager puede no estar pasando los headers necesarios para CSRF.

## SOLUCIONES

### Solución 1: Limpiar Cookies del Navegador (MÁS RÁPIDA)

#### En Chrome/Edge:
1. Presiona `F12` para abrir DevTools
2. Ve a la pestaña "Application" o "Aplicación"
3. En el menú izquierdo, expande "Cookies"
4. Haz clic en `https://certificados.transportespuno.gob.pe`
5. Elimina todas las cookies (especialmente `csrftoken` y `sessionid`)
6. Recarga la página (`Ctrl + F5`)

#### En Firefox:
1. Presiona `F12` para abrir DevTools
2. Ve a la pestaña "Storage" o "Almacenamiento"
3. Expande "Cookies"
4. Haz clic en `https://certificados.transportespuno.gob.pe`
5. Elimina todas las cookies
6. Recarga la página (`Ctrl + F5`)

#### Método Alternativo:
- Abre una ventana de **Incógnito/Privada** y prueba acceder al admin

### Solución 2: Configurar Headers en Nginx Proxy Manager

1. Accede a Nginx Proxy Manager
2. Edita el Proxy Host para `certificados.transportespuno.gob.pe`
3. Ve a la pestaña "Custom locations" o "Advanced"
4. Agrega estas configuraciones en "Custom Nginx Configuration":

```nginx
# Headers para CSRF
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-Host $host;
proxy_set_header X-Forwarded-Port $server_port;

# Headers adicionales para Django
proxy_set_header X-Forwarded-Ssl on;
proxy_redirect off;
```

5. Guarda los cambios

### Solución 3: Reiniciar Completamente (SI LAS ANTERIORES NO FUNCIONAN)

Ejecuta estos comandos en el servidor:

```bash
ssh administrador@161.132.47.92
cd dockers/sistema_certificados_drtc

# Reiniciar todo
docker compose down
docker compose up -d

# Esperar 20 segundos
sleep 20

# Verificar logs
docker compose logs --tail=20 web
```

### Solución 4: Verificar Configuración de Nginx Proxy Manager

Asegúrate de que en Nginx Proxy Manager:

1. **SSL Tab**:
   - ✅ Force SSL: Activado
   - ✅ HTTP/2 Support: Activado
   - ✅ HSTS Enabled: Activado (opcional)

2. **Details Tab**:
   - Scheme: `http`
   - Forward Hostname/IP: `161.132.47.92`
   - Forward Port: `7070`
   - ✅ Cache Assets: Desactivado (importante)
   - ✅ Block Common Exploits: Activado
   - ✅ Websockets Support: Activado (opcional)

3. **Advanced Tab**:
   Agregar:
   ```nginx
   location / {
       proxy_pass http://161.132.47.92:7070;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
       proxy_set_header X-Forwarded-Host $host;
   }
   ```

## Verificación Final

Después de aplicar cualquiera de las soluciones:

1. Abre una ventana de incógnito
2. Accede a: `https://certificados.transportespuno.gob.pe/admin/`
3. Deberías ver el formulario de login sin error 403

## Comandos de Diagnóstico

### Ver configuración actual de Django:
```bash
ssh administrador@161.132.47.92
cd dockers/sistema_certificados_drtc
echo 'from django.conf import settings; print(settings.ALLOWED_HOSTS); print(settings.CSRF_TRUSTED_ORIGINS)' | docker compose exec -T web python manage.py shell
```

### Ver logs en tiempo real:
```bash
docker compose logs -f web
```

### Probar desde el servidor:
```bash
curl -I https://certificados.transportespuno.gob.pe/admin/
```

## Solución Definitiva (SI NADA FUNCIONA)

Si ninguna de las soluciones anteriores funciona, el problema puede estar en que Django necesita confiar en el proxy. Agrega esto al `.env.production`:

```bash
# Confiar en el proxy
USE_X_FORWARDED_HOST=True
USE_X_FORWARDED_PORT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
```

Luego ejecuta:
```bash
ssh administrador@161.132.47.92
cd dockers/sistema_certificados_drtc

# Agregar las variables
echo "" >> .env.production
echo "# Proxy settings" >> .env.production
echo "USE_X_FORWARDED_HOST=True" >> .env.production
echo "USE_X_FORWARDED_PORT=True" >> .env.production

# Reiniciar
docker compose down && docker compose up -d
```

## Resumen de Pasos Recomendados

1. ✅ **PRIMERO**: Limpia las cookies del navegador o usa incógnito
2. ✅ **SEGUNDO**: Verifica la configuración de Nginx Proxy Manager
3. ✅ **TERCERO**: Agrega los headers en Nginx Proxy Manager
4. ✅ **CUARTO**: Reinicia los contenedores si es necesario

---

**La solución más común es simplemente limpiar las cookies del navegador** 🍪
