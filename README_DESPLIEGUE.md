# 🚀 Despliegue a Producción - Guía Rápida

## ⚡ EJECUTAR AHORA

### Opción 1: Script Automatizado (MÁS FÁCIL)

Doble clic en:
```
EJECUTA_ESTOS_COMANDOS.bat
```

O desde terminal:
```cmd
EJECUTA_ESTOS_COMANDOS.bat
```

### Opción 2: Comandos Manuales

```cmd
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache web
docker compose -f docker-compose.prod.yml up -d
```

---

## ✅ Verificar que Funciona

```cmd
docker compose -f docker-compose.prod.yml ps
```

Deberías ver todos los servicios "Up" o "Up (healthy)".

---

## 🌐 Acceder a la Aplicación

Una vez desplegado, abre en tu navegador:

- 🏠 **Página principal:** http://localhost/
- 👤 **Admin:** http://localhost/admin/
- ❤️ **Health check:** http://localhost/health/
- 🔌 **API:** http://localhost/api/

---

## 📊 Ver Logs

```cmd
docker compose -f docker-compose.prod.yml logs -f
```

Presiona `Ctrl+C` para salir.

---

## 🔄 Comandos Útiles

```cmd
REM Ver estado
docker compose -f docker-compose.prod.yml ps

REM Reiniciar
docker compose -f docker-compose.prod.yml restart

REM Detener
docker compose -f docker-compose.prod.yml stop

REM Ver logs
docker compose -f docker-compose.prod.yml logs -f
```

---

## 🔧 Problema Solucionado

### ❌ Error Original
```
exec: "/app/entrypoint.sh": permission denied
```

### ✅ Solución Aplicada
- Actualizado `Dockerfile` con permisos correctos
- Agregado `chmod +x` para `entrypoint.sh`
- Todos los scripts actualizados a Docker Compose v2

---

## 💡 Importante: Docker Compose v2

### ❌ Antiguo (NO usar)
```cmd
docker-compose -f docker-compose.prod.yml up -d
```

### ✅ Nuevo (USAR)
```cmd
docker compose -f docker-compose.prod.yml up -d
```

**Diferencia:** Sin guión entre `docker` y `compose`.

---

## 📚 Documentación Completa

### Guías Rápidas
- 📄 `DESPLEGAR_AHORA.md` - Comandos inmediatos
- 📄 `EJECUTAR_AHORA.md` - Solución rápida
- 📄 `RESUMEN_DESPLIEGUE_2025.md` - Resumen completo

### Guías Detalladas
- 📘 `COMANDOS_PRODUCCION_2025.md` - Todos los comandos
- 📘 `DESPLIEGUE_PRODUCCION_COMPLETO.md` - Guía paso a paso
- 📘 `CHECKLIST_DESPLIEGUE.md` - Checklist completo

### Scripts
- 🔧 `EJECUTA_ESTOS_COMANDOS.bat` - Script interactivo
- 🔧 `deploy-production.bat` - Script completo

---

## 🚨 Si Algo Sale Mal

### 1. Ver Logs Detallados
```cmd
docker compose -f docker-compose.prod.yml logs --tail=100
```

### 2. Reiniciar Todo
```cmd
docker compose -f docker-compose.prod.yml restart
```

### 3. Reconstruir Desde Cero
```cmd
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

---

## 🎯 Checklist Rápido

- [ ] Docker Desktop corriendo
- [ ] Archivo `.env.production` configurado
- [ ] Ejecutar `EJECUTA_ESTOS_COMANDOS.bat`
- [ ] Verificar servicios con `docker compose ps`
- [ ] Abrir http://localhost/ en navegador
- [ ] Iniciar sesión en admin
- [ ] ¡Listo! 🎉

---

## 📞 Ayuda

Si necesitas ayuda:

1. **Ver logs:**
   ```cmd
   docker compose -f docker-compose.prod.yml logs -f
   ```

2. **Verificar estado:**
   ```cmd
   docker compose -f docker-compose.prod.yml ps
   ```

3. **Consultar documentación:**
   - `COMANDOS_PRODUCCION_2025.md`
   - `DESPLIEGUE_PRODUCCION_COMPLETO.md`

---

## ✨ Resumen

1. ✅ Error de permisos solucionado
2. ✅ Scripts actualizados a Docker Compose v2
3. ✅ Documentación completa creada
4. ✅ Listo para desplegar

**Ejecuta:**
```cmd
EJECUTA_ESTOS_COMANDOS.bat
```

**O manualmente:**
```cmd
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache web
docker compose -f docker-compose.prod.yml up -d
```

---

**Última actualización:** 2025-11-10  
**Versión:** Docker Compose v2  
**Estado:** ✅ Listo para producción
