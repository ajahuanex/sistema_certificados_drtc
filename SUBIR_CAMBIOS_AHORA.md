# 🚀 Subir Cambios a GitHub - EJECUTAR AHORA

## 📋 Archivos que necesitamos subir:
1. `config/settings/production.py` - HiredisParser removido
2. `nginx.prod.simple.conf` - Configuración nginx sin SSL

## 🔄 Comandos para Windows (tu máquina local):

```bash
# 1. Ver qué archivos han cambiado
git status

# 2. Agregar los archivos
git add config/settings/production.py nginx.prod.simple.conf

# 3. Commit
git commit -m "fix: Remove HiredisParser and add simple nginx config without SSL"

# 4. Push a GitHub
git push origin main
```

## ⚠️ Si Git pide autenticación:
- **Usuario**: ajahuanex
- **Password**: Usa un Personal Access Token (no tu contraseña de GitHub)

### Cómo crear un Personal Access Token:
1. Ve a: https://github.com/settings/tokens
2. Click en "Generate new token" → "Generate new token (classic)"
3. Dale un nombre: "Ubuntu Server"
4. Selecciona: `repo` (todos los permisos de repositorio)
5. Click en "Generate token"
6. **COPIA EL TOKEN** (solo se muestra una vez)
7. Usa ese token como contraseña cuando Git te lo pida

---

## 🐧 Después en Ubuntu:

```bash
# 1. Ir al directorio
cd ~/dockers

# 2. Hacer backup del directorio actual
mv sistema_certificados_drtc sistema_certificados_drtc_backup

# 3. Clonar de nuevo
git clone https://github.com/ajahuanex/sistema_certificados_drtc.git

# 4. Entrar al directorio
cd sistema_certificados_drtc

# 5. Copiar el .env.production del backup
cp ../sistema_certificados_drtc_backup/.env.production .

# 6. Copiar la configuración simple como nginx.prod.conf
cp nginx.prod.simple.conf nginx.prod.conf

# 7. Iniciar los servicios
docker compose -f docker-compose.prod.yml --env-file .env.production up -d

# 8. Ver logs
docker compose -f docker-compose.prod.yml --env-file .env.production logs -f
```

---

## ✅ Verificación Final

```bash
# Ver estado de servicios
docker compose -f docker-compose.prod.yml --env-file .env.production ps

# Probar health check
curl http://localhost:7070/health/
```

---

**EJECUTA PRIMERO LOS COMANDOS DE WINDOWS, LUEGO LOS DE UBUNTU** 🚀
