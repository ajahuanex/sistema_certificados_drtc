# 🚨 SOLUCIÓN ERROR 502 - BAD GATEWAY

## El Problema
HTTP 502 significa que el proxy no puede conectar con Django. Probablemente causado por `SECURE_SSL_REDIRECT=True` creando bucles de redirección.

## Solución Inmediata

### 1. Deshabilitar SSL redirect temporalmente
```bash
# En el servidor
cd sistema_certificados_drtc

# Editar .env.production para deshabilitar SSL redirect
sed -i 's/SECURE_SSL_REDIRECT=True/SECURE_SSL_REDIRECT=False/' .env.production

# Reiniciar
docker compose restart web

# Probar localmente primero
curl -I http://localhost:7070/admin/
```

### 2. Si funciona localmente, probar HTTPS
```bash
curl -I https://certificados.transportespuno.gob.pe/admin/
```

### 3. Ver logs para diagnosticar
```bash
docker compose logs web --tail=20
```

## Configuración Correcta para HTTPS con Proxy

El problema es que cuando usas un proxy inverso (como Nginx Proxy Manager), Django no debe manejar la redirección SSL - eso lo hace el proxy.

### Configuración recomendada:
```bash
# Mantener estas configuraciones
SECURE_SSL_REDIRECT=False  # ← El proxy maneja esto
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=0      # ← El proxy maneja esto
```