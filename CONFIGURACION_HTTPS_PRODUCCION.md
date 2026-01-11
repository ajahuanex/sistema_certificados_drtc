# 🔒 CONFIGURACIÓN HTTPS PARA PRODUCCIÓN

## Situación Actual
- Estás accediendo con HTTPS: https://certificados.transportespuno.gob.pe
- Necesitamos ajustar configuraciones de seguridad para SSL

## Comandos para ejecutar en el servidor

### 1. Conectar al servidor
```bash
ssh administrador@161.132.47.92
cd sistema_certificados_drtc
```

### 2. Actualizar configuraciones HTTPS en .env.production
```bash
# Hacer backup del archivo actual
cp .env.production .env.production.backup

# Actualizar configuraciones para HTTPS
cat >> .env.production << 'EOF'

# HTTPS Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SECURE_CROSS_ORIGIN_OPENER_POLICY=same-origin
EOF
```

### 3. Reiniciar la aplicación
```bash
docker compose restart web
```

### 4. Verificar configuración
```bash
# Ver las nuevas configuraciones
tail -10 .env.production

# Probar HTTPS
curl -I https://certificados.transportespuno.gob.pe/admin/
```

## ¿Qué hace cada configuración?

- `SECURE_SSL_REDIRECT=True`: Redirige HTTP a HTTPS automáticamente
- `SESSION_COOKIE_SECURE=True`: Las cookies de sesión solo se envían por HTTPS
- `CSRF_COOKIE_SECURE=True`: Las cookies CSRF solo se envían por HTTPS
- `SECURE_HSTS_SECONDS=31536000`: Fuerza HTTPS por 1 año
- `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`: Aplica HSTS a subdominios
- `SECURE_HSTS_PRELOAD=True`: Permite precargar en navegadores

## Resultado Esperado
- Mejor seguridad con HTTPS
- Redirección automática de HTTP a HTTPS
- Cookies más seguras
- Cumplimiento de estándares de seguridad web