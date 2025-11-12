# 📤 Guía de Actualización de GitHub

## ✅ Cambios Realizados

### 1. Dockerfile
- ✅ Agregado `chmod +x` para `entrypoint.sh`
- ✅ Permisos configurados correctamente

### 2. Scripts
- ✅ Actualizados a Docker Compose v2 (sin guión)
- ✅ `deploy-production.bat`
- ✅ `EJECUTA_ESTOS_COMANDOS.bat`
- ✅ Todos los scripts de documentación

### 3. Variables de Entorno
- ✅ Dominio actualizado a `certificados.transportespuno.gob.pe`
- ✅ `.env.production.example` actualizado
- ✅ `.env.production` actualizado

### 4. Documentación
- ✅ 8+ archivos de documentación creados
- ✅ Guías rápidas y completas
- ✅ Scripts automatizados

---

## 🚀 Actualizar GitHub - Opción 1: Script Automatizado

### Ejecutar el Script

```cmd
actualizar-github.bat
```

Este script:
1. Verifica que estás en un repositorio Git
2. Muestra el estado actual
3. Agrega todos los cambios
4. Crea un commit con mensaje descriptivo
5. Hace push a GitHub

---

## 🔧 Actualizar GitHub - Opción 2: Manual

### Paso 1: Verificar Estado

```cmd
git status
```

### Paso 2: Agregar Cambios

```cmd
git add .
```

### Paso 3: Crear Commit

```cmd
git commit -m "Actualización: Docker Compose v2, corrección permisos entrypoint.sh, dominio transportespuno.gob.pe"
```

### Paso 4: Push a GitHub

```cmd
git push origin main
```

O si tu rama es `master`:

```cmd
git push origin master
```

---

## 📋 Archivos Principales Actualizados

### Archivos de Configuración
- ✅ `Dockerfile` - Permisos de entrypoint corregidos
- ✅ `.env.production` - Dominio actualizado
- ✅ `.env.production.example` - Dominio actualizado
- ✅ `docker-compose.prod.yml` - Sin cambios necesarios

### Scripts de Despliegue
- ✅ `deploy-production.bat` - Docker Compose v2
- ✅ `EJECUTA_ESTOS_COMANDOS.bat` - Docker Compose v2
- ✅ `actualizar-github.bat` - Nuevo script

### Documentación Nueva
- ✅ `README_DESPLIEGUE.md` - Guía principal
- ✅ `DESPLEGAR_AHORA.md` - Comandos rápidos
- ✅ `COMANDOS_PRODUCCION_2025.md` - Referencia completa
- ✅ `RESUMEN_DESPLIEGUE_2025.md` - Resumen
- ✅ `EJECUTAR_AHORA.md` - Solución inmediata
- ✅ `SOLUCION_RAPIDA_PRODUCCION.md` - Troubleshooting
- ✅ `CHECKLIST_DESPLIEGUE.md` - Checklist
- ✅ `DESPLIEGUE_PRODUCCION_COMPLETO.md` - Guía detallada

---

## 🌐 Configuración del Dominio

### Dominio Configurado

```
certificados.transportespuno.gob.pe
```

### Archivos Actualizados

#### .env.production
```env
ALLOWED_HOSTS=localhost,127.0.0.1,certificados.transportespuno.gob.pe,www.certificados.transportespuno.gob.pe
SITE_URL=http://localhost
INSTITUTION_NAME=Dirección Regional de Transportes y Comunicaciones - Puno
INSTITUTION_EMAIL=info@transportespuno.gob.pe
```

#### .env.production.example
```env
ALLOWED_HOSTS=certificados.transportespuno.gob.pe,www.certificados.transportespuno.gob.pe,localhost,127.0.0.1
SITE_URL=https://certificados.transportespuno.gob.pe
CSRF_TRUSTED_ORIGINS=https://certificados.transportespuno.gob.pe,https://www.certificados.transportespuno.gob.pe
CORS_ALLOWED_ORIGINS=https://certificados.transportespuno.gob.pe,https://www.certificados.transportespuno.gob.pe
```

---

## 🔐 Configuración para Producción Real

Cuando despliegues en el servidor real con el dominio, actualiza `.env.production`:

```env
# Cambiar de localhost a dominio real
SITE_URL=https://certificados.transportespuno.gob.pe

# Habilitar HTTPS
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Configurar CSRF y CORS
CSRF_TRUSTED_ORIGINS=https://certificados.transportespuno.gob.pe,https://www.certificados.transportespuno.gob.pe
CORS_ALLOWED_ORIGINS=https://certificados.transportespuno.gob.pe,https://www.certificados.transportespuno.gob.pe
```

---

## 📝 Mensaje de Commit Sugerido

```
Actualización: Docker Compose v2, corrección permisos entrypoint.sh, dominio transportespuno.gob.pe

Cambios principales:
- Dockerfile: Agregado chmod +x para entrypoint.sh
- Scripts: Actualizados a Docker Compose v2 (sin guión)
- Variables: Dominio actualizado a certificados.transportespuno.gob.pe
- Documentación: Guías completas de despliegue creadas
- Scripts: deploy-production.bat y EJECUTA_ESTOS_COMANDOS.bat actualizados

Archivos nuevos:
- README_DESPLIEGUE.md
- COMANDOS_PRODUCCION_2025.md
- DESPLEGAR_AHORA.md
- RESUMEN_DESPLIEGUE_2025.md
- actualizar-github.bat
- EJECUTA_ESTOS_COMANDOS.bat
- Y más documentación

Correcciones:
- Error "permission denied" en entrypoint.sh solucionado
- Sintaxis Docker Compose actualizada de docker-compose a docker compose
- Configuración de dominio institucional
```

---

## 🔍 Verificar Antes de Push

### 1. Ver Cambios

```cmd
git status
git diff
```

### 2. Ver Archivos que se Agregarán

```cmd
git add .
git status
```

### 3. Verificar Commit

```cmd
git log -1
```

---

## 🚨 Troubleshooting

### Error: "No tienes permisos"

Si ves un error de permisos al hacer push:

```cmd
REM Verificar remote
git remote -v

REM Si no hay remote, agregarlo
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git

REM Configurar credenciales
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

### Error: "Authentication failed"

Necesitas configurar autenticación:

**Opción 1: Token de GitHub**
1. Ve a GitHub → Settings → Developer settings → Personal access tokens
2. Genera un nuevo token con permisos de repo
3. Usa el token como contraseña al hacer push

**Opción 2: SSH**
```cmd
REM Generar clave SSH
ssh-keygen -t ed25519 -C "tu@email.com"

REM Agregar a GitHub
REM Copia el contenido de ~/.ssh/id_ed25519.pub
REM Pégalo en GitHub → Settings → SSH keys
```

### Error: "Divergent branches"

Si hay conflictos:

```cmd
REM Opción 1: Pull primero
git pull origin main --rebase

REM Opción 2: Force push (cuidado!)
git push origin main --force
```

---

## ✅ Checklist de Actualización

- [ ] Verificar que estás en el directorio correcto
- [ ] Ejecutar `git status` para ver cambios
- [ ] Revisar archivos modificados
- [ ] Ejecutar `actualizar-github.bat` o comandos manuales
- [ ] Verificar que el push fue exitoso
- [ ] Verificar en GitHub que los cambios están ahí
- [ ] Clonar en otro lugar para probar (opcional)

---

## 🎯 Próximos Pasos Después del Push

### 1. En el Servidor de Producción

```bash
# Conectar al servidor
ssh usuario@servidor

# Ir al directorio del proyecto
cd /ruta/al/proyecto

# Hacer pull de los cambios
git pull origin main

# Reconstruir y desplegar
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

### 2. Configurar DNS

Asegúrate de que el dominio `certificados.transportespuno.gob.pe` apunte a tu servidor:

- Tipo: A Record
- Host: certificados
- Valor: IP del servidor
- TTL: 3600

### 3. Configurar SSL/HTTPS

Una vez que el dominio esté configurado, instala certificado SSL:

```bash
# Usando Let's Encrypt
certbot --nginx -d certificados.transportespuno.gob.pe
```

---

## 📞 Ayuda

Si tienes problemas:

1. **Ver logs de Git:**
   ```cmd
   git log --oneline -10
   ```

2. **Ver remote configurado:**
   ```cmd
   git remote -v
   ```

3. **Ver rama actual:**
   ```cmd
   git branch
   ```

4. **Deshacer último commit (si es necesario):**
   ```cmd
   git reset --soft HEAD~1
   ```

---

**Última actualización:** 2025-11-10  
**Dominio:** certificados.transportespuno.gob.pe  
**Docker Compose:** v2 (sin guión)
