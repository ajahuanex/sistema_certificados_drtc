# ✅ SINCRONIZACIÓN COMPLETA - GitHub y Servidor Remoto

**Fecha:** 20 de Noviembre, 2025  
**Servidor:** 161.132.47.92  
**Usuario:** administrador

---

## 📦 Estado GitHub

✅ **Repositorio local sincronizado con GitHub**
- Branch: main
- Último commit: `8a7a0da - Actualización: Mejoras UI páginas públicas y documentación firma digital`
- Estado: Todo actualizado y pusheado

---

## 🖥️ Verificar Servidor Remoto

### Opción 1: Verificación Rápida (Windows)
```cmd
verificar-servidor-remoto.bat
```

### Opción 2: Verificación Rápida (Linux/Mac)
```bash
./verificar-servidor-remoto.sh
```

### Opción 3: Verificación Manual
```bash
ssh administrador@161.132.47.92 "cd sistema_certificados_drtc && git status && git log --oneline -3"
```

---

## 🔄 Actualizar Servidor Remoto

Si el servidor está desactualizado, usa estos comandos:

### Opción 1: Actualización Automática (Windows)
```cmd
actualizar-servidor-remoto.bat
```

### Opción 2: Actualización Automática (Linux/Mac)
```bash
./actualizar-servidor-remoto.sh
```

### Opción 3: Actualización Manual
```bash
# Conectar al servidor
ssh administrador@161.132.47.92

# Ir al directorio del proyecto
cd sistema_certificados_drtc

# Actualizar código
git pull origin main

# Reconstruir y reiniciar
docker compose build
docker compose up -d

# Esperar 15 segundos
sleep 15

# Aplicar migraciones y colectar estáticos
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput

# Verificar estado
docker compose ps
curl http://localhost:7070/health/
```

---

## 📊 Comandos Útiles del Servidor

### Ver logs en tiempo real
```bash
ssh administrador@161.132.47.92 "cd sistema_certificados_drtc && docker compose logs -f"
```

### Ver estado de servicios
```bash
ssh administrador@161.132.47.92 "cd sistema_certificados_drtc && docker compose ps"
```

### Ver últimos 50 logs
```bash
ssh administrador@161.132.47.92 "cd sistema_certificados_drtc && docker compose logs --tail=50"
```

### Reiniciar servicios
```bash
ssh administrador@161.132.47.92 "cd sistema_certificados_drtc && docker compose restart"
```

### Ver uso de recursos
```bash
ssh administrador@161.132.47.92 "docker stats --no-stream"
```

---

## 🌐 Acceso a la Aplicación

- **URL Directa:** http://161.132.47.92:7070/admin/
- **URL con Proxy:** http://161.132.47.92/admin/ (si nginx está configurado)
- **Usuario:** admin
- **Contraseña:** admin123

---

## 🔐 Cambiar Contraseña de Admin

```bash
ssh administrador@161.132.47.92 "cd sistema_certificados_drtc && docker compose exec web python manage.py changepassword admin"
```

---

## 📝 Archivos Actualizados

Los siguientes scripts ahora usan el usuario `administrador`:

1. ✅ `verificar-servidor-remoto.bat`
2. ✅ `verificar-servidor-remoto.sh`
3. ✅ `actualizar-servidor-remoto.bat`
4. ✅ `actualizar-servidor-remoto.sh`
5. ✅ `DESPLIEGUE_FINAL_7070.txt`

---

## 🚀 Flujo de Trabajo Recomendado

1. **Hacer cambios locales** → Editar código
2. **Commit local** → `git add . && git commit -m "mensaje"`
3. **Push a GitHub** → `git push origin main`
4. **Verificar servidor** → `verificar-servidor-remoto.bat`
5. **Actualizar servidor** → `actualizar-servidor-remoto.bat`
6. **Verificar funcionamiento** → Abrir http://161.132.47.92:7070/admin/

---

## ⚠️ Notas Importantes

- Siempre verifica el estado del servidor antes de actualizar
- Los scripts automáticos esperan 15 segundos para que los servicios se inicien
- Si hay errores, revisa los logs con `docker compose logs`
- Mantén backups regulares de la base de datos
- El puerto 7070 está configurado para trabajar con nginx proxy inverso

---

## 📞 Troubleshooting

### Si el servidor no responde:
```bash
ssh administrador@161.132.47.92 "cd sistema_certificados_drtc && docker compose ps"
```

### Si hay errores en los contenedores:
```bash
ssh administrador@161.132.47.92 "cd sistema_certificados_drtc && docker compose logs --tail=100"
```

### Si necesitas reiniciar todo:
```bash
ssh administrador@161.132.47.92 "cd sistema_certificados_drtc && docker compose down && docker compose up -d"
```

### Si necesitas limpiar y reconstruir:
```bash
ssh administrador@161.132.47.92 "cd sistema_certificados_drtc && docker compose down -v && docker compose build --no-cache && docker compose up -d"
```

---

✅ **Todo listo para mantener sincronizado GitHub y el servidor remoto**
