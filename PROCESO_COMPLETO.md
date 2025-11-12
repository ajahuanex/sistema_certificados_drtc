# 📋 Proceso Completo: Windows → GitHub → Ubuntu

## 🎯 Objetivo

Subir los cambios desde Windows a GitHub, y luego actualizar en tu servidor Ubuntu.

---

## 📍 PARTE 1: Subir a GitHub (Desde Windows)

### Opción A: Script Automatizado

```cmd
subir-a-github.bat
```

### Opción B: Comandos Manuales

```cmd
REM 1. Ver estado
git status

REM 2. Agregar todos los cambios
git add .

REM 3. Crear commit
git commit -m "Actualización: Docker Compose v2, corrección permisos, dominio transportespuno.gob.pe"

REM 4. Ver rama actual
git branch

REM 5. Hacer push
git push origin main
```

O si tu rama es `master`:
```cmd
git push origin master
```

### Verificar en GitHub

1. Abre tu repositorio en GitHub
2. Verifica que los cambios estén ahí
3. Busca estos archivos nuevos:
   - `deploy-ubuntu.sh`
   - `EJECUTA_EN_UBUNTU.md`
   - `DESPLIEGUE_UBUNTU.md`
   - `COMANDOS_UBUNTU.md`

---

## 🐧 PARTE 2: Actualizar en Ubuntu (Desde Servidor)

### Paso 1: Conectar al Servidor

```bash
ssh usuario@tu-servidor
```

### Paso 2: Ir al Directorio del Proyecto

```bash
cd /ruta/al/proyecto
```

Si no recuerdas la ruta:
```bash
# Buscar el proyecto
find ~ -name "docker-compose.prod.yml" 2>/dev/null
```

### Paso 3: Actualizar desde GitHub

```bash
# Ver estado actual
git status

# Actualizar código
git pull origin main
```

O si tu rama es `master`:
```bash
git pull origin master
```

### Paso 4: Dar Permisos al Script

```bash
chmod +x deploy-ubuntu.sh
```

### Paso 5: Ejecutar Despliegue

```bash
./deploy-ubuntu.sh
```

El script hará todo automáticamente:
- ✅ Verifica Docker
- ✅ Detiene servicios anteriores
- ✅ Construye nuevas imágenes
- ✅ Inicia servicios
- ✅ Verifica que todo funcione

---

## ✅ Verificación

### En Ubuntu, verifica:

```bash
# 1. Estado de servicios
docker compose -f docker-compose.prod.yml ps

# 2. Logs
docker compose -f docker-compose.prod.yml logs --tail=50

# 3. Health check
curl http://localhost/health/
```

### Deberías ver:

```
NAME                          STATUS
certificados_db_prod          Up (healthy)
certificados_redis_prod       Up (healthy)
certificados_web_prod         Up
certificados_nginx_prod       Up
```

---

## 📊 Resumen de Cambios Subidos

### Archivos Principales

1. **Dockerfile**
   - ✅ Agregado `chmod +x` para `entrypoint.sh`
   - ✅ Error "permission denied" solucionado

2. **Variables de Entorno**
   - ✅ `.env.production` - Dominio actualizado
   - ✅ `.env.production.example` - Dominio actualizado
   - ✅ Dominio: `certificados.transportespuno.gob.pe`

3. **Scripts**
   - ✅ Todos actualizados a Docker Compose v2
   - ✅ `deploy-ubuntu.sh` - Nuevo script para Ubuntu
   - ✅ `deploy-production.bat` - Actualizado para Windows

4. **Documentación**
   - ✅ `EJECUTA_EN_UBUNTU.md` - Guía rápida Ubuntu
   - ✅ `DESPLIEGUE_UBUNTU.md` - Guía completa Ubuntu
   - ✅ `COMANDOS_UBUNTU.md` - Referencia de comandos
   - ✅ `PROCESO_COMPLETO.md` - Este archivo
   - ✅ Y 10+ archivos más de documentación

---

## 🔄 Flujo Completo

```
┌─────────────┐
│   Windows   │
│  (Desarrollo)│
└──────┬──────┘
       │
       │ git push
       ▼
┌─────────────┐
│   GitHub    │
│ (Repositorio)│
└──────┬──────┘
       │
       │ git pull
       ▼
┌─────────────┐
│   Ubuntu    │
│  (Servidor) │
└─────────────┘
```

---

## 🚨 Troubleshooting

### Error en Windows: "Permission denied" al hacer push

**Solución:**
```cmd
REM Configurar credenciales
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"

REM Usar token de GitHub como contraseña
REM Ve a: GitHub → Settings → Developer settings → Personal access tokens
```

### Error en Ubuntu: "Permission denied" en deploy-ubuntu.sh

**Solución:**
```bash
chmod +x deploy-ubuntu.sh
```

### Error en Ubuntu: "Cannot connect to Docker daemon"

**Solución:**
```bash
# Iniciar Docker
sudo systemctl start docker

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

### Error: "Divergent branches"

**Solución:**
```bash
# En Ubuntu
git pull origin main --rebase
```

---

## 📝 Comandos de Referencia Rápida

### Windows

```cmd
REM Subir a GitHub
subir-a-github.bat

REM O manualmente
git add .
git commit -m "Tu mensaje"
git push origin main
```

### Ubuntu

```bash
# Actualizar y desplegar
cd /ruta/al/proyecto
git pull origin main
chmod +x deploy-ubuntu.sh
./deploy-ubuntu.sh

# Ver estado
docker compose -f docker-compose.prod.yml ps

# Ver logs
docker compose -f docker-compose.prod.yml logs -f
```

---

## 🎯 Checklist Completo

### En Windows
- [ ] Ejecutar `subir-a-github.bat` o comandos manuales
- [ ] Verificar push exitoso
- [ ] Verificar cambios en GitHub

### En Ubuntu
- [ ] Conectar al servidor por SSH
- [ ] Ir al directorio del proyecto
- [ ] Ejecutar `git pull origin main`
- [ ] Dar permisos: `chmod +x deploy-ubuntu.sh`
- [ ] Ejecutar `./deploy-ubuntu.sh`
- [ ] Verificar servicios corriendo
- [ ] Verificar logs sin errores
- [ ] Probar acceso web

---

## 🌐 Acceso Final

Una vez desplegado en Ubuntu:

- **HTTP:** http://TU_IP_SERVIDOR/
- **HTTPS:** https://certificados.transportespuno.gob.pe/ (con SSL)
- **Admin:** https://certificados.transportespuno.gob.pe/admin/
- **Health:** https://certificados.transportespuno.gob.pe/health/

---

## 📚 Documentación Adicional

### Para Windows
- `README_DESPLIEGUE.md` - Guía principal
- `COMANDOS_PRODUCCION_2025.md` - Referencia de comandos
- `deploy-production.bat` - Script de despliegue

### Para Ubuntu
- `EJECUTA_EN_UBUNTU.md` - **EMPIEZA AQUÍ**
- `DESPLIEGUE_UBUNTU.md` - Guía completa
- `COMANDOS_UBUNTU.md` - Referencia de comandos
- `deploy-ubuntu.sh` - Script de despliegue

---

## ✨ Próximos Pasos

Después de desplegar en Ubuntu:

1. **Configurar DNS** - Apuntar dominio a tu servidor
2. **Configurar SSL** - Instalar certificado HTTPS
3. **Configurar Backups** - Backups automáticos de BD
4. **Monitoreo** - Configurar alertas y logs

---

**Última actualización:** 2025-11-10  
**Dominio:** certificados.transportespuno.gob.pe  
**Docker Compose:** v2 (sin guión)  
**Estado:** ✅ Listo para subir a GitHub
