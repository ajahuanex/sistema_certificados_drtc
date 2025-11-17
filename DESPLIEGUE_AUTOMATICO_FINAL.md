# 🚀 Despliegue Automático Final

## Proceso Completo en 2 Pasos

### ✅ PASO 1: Subir a GitHub (Windows)

Ejecuta este comando en tu terminal de Windows:

```batch
SUBIR_A_GITHUB_AHORA.bat
```

O manualmente:

```bash
git update-index --chmod=+x entrypoint.sh
git update-index --chmod=+x verificar-y-desplegar.sh
git add .
git commit -m "Fix: Nginx HTTP config, permisos y script de despliegue automatico"
git push origin main
```

---

### ✅ PASO 2: Desplegar en Ubuntu (Automático)

Conéctate al servidor y ejecuta:

```bash
# Conectar al servidor
ssh usuario@161.132.47.92

# Ir al directorio del proyecto
cd ~/drtc_certificados

# Actualizar código
git pull origin main

# Dar permisos al script
chmod +x verificar-y-desplegar.sh

# Ejecutar despliegue automático
./verificar-y-desplegar.sh
```

---

## 🎯 ¿Qué hace el script automático?

El script `verificar-y-desplegar.sh` realiza automáticamente:

1. ✅ **Verifica puertos** (7070, 5433, 6380)
2. ✅ **Detiene contenedores** si hay conflictos
3. ✅ **Verifica archivos** necesarios
4. ✅ **Da permisos** a entrypoint.sh
5. ✅ **Hace backup** de .env.production
6. ✅ **Construye imágenes** Docker
7. ✅ **Levanta servicios** (db, redis, web, nginx)
8. ✅ **Configura nginx** con HTTP
9. ✅ **Recolecta archivos estáticos**
10. ✅ **Verifica** que todo funcione

---

## 📊 Salida Esperada

Verás algo como esto:

```
============================================
VERIFICACIÓN Y DESPLIEGUE AUTOMÁTICO
Sistema de Certificados DRTC
============================================

📋 PASO 1: Verificando puertos...
✅ Puerto 7070 está libre
✅ Puerto 5433 está libre
✅ Puerto 6380 está libre

📋 PASO 2: Verificando archivos necesarios...
✅ .env.production encontrado
✅ docker-compose.prod.yml encontrado
✅ nginx.prod.http-only.conf encontrado
✅ entrypoint.sh encontrado

📋 PASO 3: Configurando permisos...
✅ Permisos de ejecución dados a entrypoint.sh

📋 PASO 4: Haciendo backup de configuración...
✅ Backup creado: .env.production.backup.20250112_143022

📋 PASO 5: Construyendo imágenes Docker...
✅ Imagen web construida

📋 PASO 6: Levantando servicios...
✅ Servicios levantados

📋 PASO 7: Esperando a que los servicios inicien...
✅ Servicios iniciados

📋 PASO 8: Verificando estado de contenedores...
NAME                    STATUS              PORTS
certificados-drtc-db-1      Up 30 seconds       0.0.0.0:5433->5432/tcp
certificados-drtc-redis-1   Up 30 seconds       0.0.0.0:6380->6379/tcp
certificados-drtc-web-1     Up 30 seconds       8000/tcp
certificados-drtc-nginx-1   Up 30 seconds       0.0.0.0:7070->80/tcp

📋 PASO 9: Configurando nginx...
Contenedor nginx: certificados-drtc-nginx-1
✅ Configuración nginx copiada
✅ Configuración nginx válida

📋 PASO 10: Recolectando archivos estáticos...
✅ Archivos estáticos recolectados

📋 PASO 11: Recargando nginx...
✅ Nginx recargado

📋 PASO 12: Verificación final...
✅ Archivos estáticos verificados

============================================
✅ DESPLIEGUE COMPLETADO EXITOSAMENTE
============================================

🌐 Acceso a la aplicación:
   URL: http://161.132.47.92:7070/admin/
   Usuario: admin
   Contraseña: admin123

📊 Comandos útiles:
   Ver logs: docker compose -f docker-compose.prod.yml --env-file .env.production logs -f
   Ver estado: docker compose -f docker-compose.prod.yml --env-file .env.production ps
   Reiniciar: docker compose -f docker-compose.prod.yml --env-file .env.production restart

🎉 ¡Listo para usar!
```

---

## 🔧 Si algo falla

### El script detecta puertos ocupados

El script te preguntará:
```
⚠️  Algunos puertos están ocupados

Opciones:
1. Detener contenedores existentes y continuar
2. Cancelar despliegue

Selecciona una opción (1/2):
```

Selecciona `1` para continuar.

### Faltan archivos

Si ves:
```
❌ Falta archivo: .env.production
```

Ejecuta:
```bash
git pull origin main
```

### Error en construcción de imagen

Si falla en el PASO 5, verifica los logs:
```bash
docker compose -f docker-compose.prod.yml --env-file .env.production logs web
```

---

## 📝 Despliegue Manual (Si prefieres)

Si prefieres hacerlo paso a paso manualmente, usa:

```
DESPLIEGUE_PASO_A_PASO.md
```

O los comandos de:

```
ACTUALIZAR_EN_UBUNTU.txt
```

---

## 🎯 Verificación Post-Despliegue

### 1. Verificar en navegador

Abre: **http://161.132.47.92:7070/admin/**

Deberías ver:
- ✅ Página de login de Django
- ✅ Estilos CSS aplicados correctamente
- ✅ Sin errores 404 en consola

### 2. Verificar logs

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production logs --tail=50
```

### 3. Verificar estado

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production ps
```

Todos los servicios deben estar "Up"

### 4. Probar archivo estático

```bash
curl -I http://161.132.47.92:7070/static/admin/css/base.css
```

Debe responder: `HTTP/1.1 200 OK`

---

## 🔄 Actualizaciones Futuras

Para actualizar el código en el futuro:

```bash
cd ~/drtc_certificados
git pull origin main
./verificar-y-desplegar.sh
```

El script se encargará de todo automáticamente.

---

## 📚 Documentación Adicional

- **AGREGAR_REVERSE_PROXY_DESPUES.md** - Para agregar HTTPS
- **PROCESO_COMPLETO_DESPLIEGUE.md** - Documentación técnica completa
- **DESPLIEGUE_PASO_A_PASO.md** - Guía detallada paso a paso

---

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker compose logs`
2. Verifica el estado: `docker compose ps`
3. Consulta: `DESPLIEGUE_PASO_A_PASO.md`
4. Sección de Troubleshooting

---

**¡Listo para desplegar!** 🚀

Ejecuta `SUBIR_A_GITHUB_AHORA.bat` en Windows y luego `./verificar-y-desplegar.sh` en Ubuntu.
