# 🚀 Comandos para Ejecutar en Ubuntu AHORA

## 📋 Situación Actual
- ✅ Archivo `config/settings/production.py` corregido (HiredisParser removido)
- ⚠️ Necesitas subir los cambios al servidor y reiniciar

## 🔄 Opción 1: Subir cambios con Git (RECOMENDADO)

### En tu máquina local (Windows):
```bash
# Commit y push de los cambios
git add config/settings/production.py
git commit -m "fix: Remove HiredisParser from production settings"
git push origin main
```

### En el servidor Ubuntu:
```bash
# Ir al directorio del proyecto
cd ~/dockers/sistema_certificados_drtc

# Hacer pull de los cambios
git pull origin main

# Reconstruir y reiniciar contenedores
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build

# Ver logs en tiempo real
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f web
```

---

## 🔄 Opción 2: Editar manualmente en Ubuntu

Si no quieres usar Git, edita el archivo directamente en Ubuntu:

```bash
# Ir al directorio del proyecto
cd ~/dockers/sistema_certificados_drtc

# Editar el archivo
nano config/settings/production.py
```

Busca esta sección (alrededor de la línea 40-60):
```python
'OPTIONS': {
    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
    'CONNECTION_POOL_KWARGS': {
        'max_connections': 50,
        'retry_on_timeout': True,
    },
    'SOCKET_CONNECT_TIMEOUT': 5,
    'SOCKET_TIMEOUT': 5,
    'PARSER_CLASS': 'redis.connection.HiredisParser',  # <-- ELIMINAR ESTA LÍNEA
    'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
},
```

Debe quedar así:
```python
'OPTIONS': {
    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
    'CONNECTION_POOL_KWARGS': {
        'max_connections': 50,
        'retry_on_timeout': True,
    },
    'SOCKET_CONNECT_TIMEOUT': 5,
    'SOCKET_TIMEOUT': 5,
    # HiredisParser removido - no está disponible en el contenedor
    'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
},
```

Guardar: `Ctrl+O`, Enter, `Ctrl+X`

Luego reiniciar:
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f web
```

---

## ✅ Verificación

Después de reiniciar, deberías ver en los logs:
```
✓ PostgreSQL está disponible
✓ Ejecutando migraciones
✓ Recolectando archivos estáticos
✓ Creando superusuario
✓ Starting gunicorn
```

Y NO deberías ver:
```
❌ Module "redis.connection" does not define a "HiredisParser"
```

---

## 🎯 Prueba Final

```bash
# Ver estado de servicios
docker compose -f docker-compose.prod.yml --env-file .env.production ps

# Probar health check
curl http://localhost:7070/health/

# Probar acceso a la aplicación
curl http://localhost:7070/
```

---

## 📞 Si Necesitas Ayuda

Pégame el resultado de:
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production logs web | tail -50
```
