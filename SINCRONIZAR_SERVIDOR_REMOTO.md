# 🔄 Sincronizar Servidor Remoto con GitHub

**Servidor:** 161.132.47.92  
**Usuario:** administrador  
**Ruta:** ~/dockers/sistema_certificados_drtc

---

## ⚠️ Situación Actual

✅ **GitHub:** Actualizado con último commit  
✅ **Servicios:** Corriendo correctamente en el servidor (puerto 7070)  
❌ **Repositorio Git:** Corrupto en el servidor (necesita reinicialización)

### Estado de los servicios:
```
certificados_web       Up 29 hours (healthy)   0.0.0.0:7070->8000/tcp
certificados_postgres  Up 31 hours (healthy)   5432/tcp
certificados_redis     Up 31 hours (healthy)   6379/tcp
```

---

## 🔧 Solución: Reinicializar Git en el Servidor

Conecta al servidor y ejecuta estos comandos:

```bash
# 1. Conectar al servidor
ssh administrador@161.132.47.92

# 2. Ir al directorio del proyecto
cd dockers/sistema_certificados_drtc

# 3. Eliminar .git corrupto (necesita sudo)
sudo rm -rf .git

# 4. Reinicializar repositorio
git init

# 5. Agregar remote de GitHub
git remote add origin https://github.com/ajahuanex/sistema_certificados_drtc.git

# 6. Obtener código desde GitHub
git fetch origin

# 7. Resetear a la última versión
git reset --hard origin/main

# 8. Configurar branch
git branch --set-upstream-to=origin/main main

# 9. Verificar estado
git status
git log --oneline -3
```

---

## 🔄 Actualizar Aplicación (Después de Sincronizar Git)

Una vez que el repositorio esté sincronizado:

```bash
# Reconstruir contenedores
docker compose build

# Reiniciar servicios
docker compose up -d

# Esperar 15 segundos
sleep 15

# Aplicar migraciones
docker compose exec web python manage.py migrate

# Colectar archivos estáticos
docker compose exec web python manage.py collectstatic --noinput

# Verificar estado
docker compose ps
curl http://localhost:7070/health/
```

---

## 📊 Verificar Sincronización

```bash
# Ver estado de Git
git status

# Ver últimos commits
git log --oneline -5

# Comparar con GitHub
git fetch origin
git status

# Ver diferencias (si las hay)
git diff origin/main
```

---

## 🚀 Flujo Futuro (Una vez sincronizado)

Cuando hagas cambios locales y los subas a GitHub:

```bash
# En tu máquina local
git add .
git commit -m "mensaje"
git push origin main

# En el servidor remoto
ssh administrador@161.132.47.92
cd dockers/sistema_certificados_drtc
git pull origin main
docker compose build
docker compose up -d
sleep 15
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
```

---

## 🌐 Acceso a la Aplicación

- **URL:** http://161.132.47.92:7070/admin/
- **Usuario:** admin
- **Contraseña:** admin123

---

## 📝 Notas Importantes

1. El repositorio .git estaba corrupto (probablemente por permisos)
2. Los servicios Docker están funcionando correctamente
3. No es necesario detener los servicios para sincronizar Git
4. Después de sincronizar, reconstruye los contenedores para aplicar cambios
5. Siempre haz backup antes de cambios importantes

---

## 🆘 Si Algo Sale Mal

### Backup de la base de datos:
```bash
docker compose exec postgres pg_dump -U certificados_user certificados_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Ver logs:
```bash
docker compose logs --tail=100
```

### Reiniciar todo:
```bash
docker compose restart
```

### Verificar salud de servicios:
```bash
docker compose ps
docker compose exec web python manage.py check
```

---

✅ **Ejecuta los comandos de la sección "Solución" para sincronizar el servidor con GitHub**
