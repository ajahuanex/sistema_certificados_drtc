# 🚀 Actualizar Configuración de IP en Ubuntu

## Paso 1: Subir cambios a GitHub (desde Windows)

Ejecuta el script:
```bash
SUBIR_CAMBIOS_IP.bat
```

O manualmente:
```bash
git add .env.production SOLUCION_PASSWORD_POSTGRES.md fix-postgres-password.sh
git commit -m "fix: Actualizar ALLOWED_HOSTS con IP del servidor (161.132.47.92)"
git push origin main
```

---

## Paso 2: Actualizar en Ubuntu

### 2.1 Descargar cambios de GitHub
```bash
cd ~/dockers/sistema_certificados_drtc
git pull origin main
```

### 2.2 Verificar el archivo .env.production
```bash
cat .env.production | grep ALLOWED_HOSTS
```

Debe mostrar:
```
ALLOWED_HOSTS=localhost,127.0.0.1,161.132.47.92,certificados.transportespuno.gob.pe,www.certificados.transportespuno.gob.pe
```

### 2.3 Reiniciar el servicio web
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production restart web
```

### 2.4 Verificar que funciona
```bash
# Ver logs
docker compose -f docker-compose.prod.yml --env-file .env.production logs web --tail 30

# Ver estado
docker compose -f docker-compose.prod.yml --env-file .env.production ps
```

### 2.5 Probar en el navegador

Accede a:
- **Aplicación**: http://161.132.47.92:7070
- **Admin**: http://161.132.47.92:7070/admin/
  - Usuario: `admin`
  - Contraseña: `admin123`

---

## Comandos Rápidos (Copiar y Pegar en Ubuntu)

```bash
# Ir al directorio
cd ~/dockers/sistema_certificados_drtc

# Descargar cambios
git pull origin main

# Reiniciar servicio
docker compose -f docker-compose.prod.yml --env-file .env.production restart web

# Ver logs
docker compose -f docker-compose.prod.yml --env-file .env.production logs web --tail 30

# Ver estado
docker compose -f docker-compose.prod.yml --env-file .env.production ps
```

---

## Verificación Final

Una vez reiniciado, verifica:

1. ✅ Servicios corriendo:
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production ps
```

Todos deben estar "Up" y "healthy"

2. ✅ Aplicación accesible:
```bash
curl http://161.132.47.92:7070/health/
```

Debe devolver: `{"status": "healthy"}`

3. ✅ Navegador:
- Abre http://161.132.47.92:7070
- Debe cargar la página principal sin error 400

---

## Troubleshooting

### Si sigue dando error 400:
```bash
# Ver configuración actual
docker compose -f docker-compose.prod.yml --env-file .env.production exec web python manage.py shell -c "from django.conf import settings; print(settings.ALLOWED_HOSTS)"

# Reiniciar todos los servicios
docker compose -f docker-compose.prod.yml --env-file .env.production restart
```

### Si no carga la página:
```bash
# Ver logs completos
docker compose -f docker-compose.prod.yml --env-file .env.production logs web

# Ver logs de nginx
docker compose -f docker-compose.prod.yml --env-file .env.production logs nginx
```

---

## Acceso Completo

Una vez funcionando:

- **URL Pública**: http://161.132.47.92:7070
- **Panel Admin**: http://161.132.47.92:7070/admin/
- **Health Check**: http://161.132.47.92:7070/health/
- **Consulta Certificados**: http://161.132.47.92:7070/consulta/

**Credenciales Admin:**
- Usuario: `admin`
- Contraseña: `admin123`

---

¡Listo! Tu aplicación estará accesible desde cualquier lugar usando la IP pública. 🎉
