# 🔄 Guía Rápida: Sistema de Rollback

## Comandos Rápidos

### Despliegue con Rollback Automático

```bash
# Linux/Mac
./update-production.sh

# Windows
update-production.bat
```

### Rollback Manual

```bash
# Linux/Mac - Rollback rápido (último commit + último backup)
./rollback.sh --quick

# Linux/Mac - Menú interactivo
./rollback.sh

# Windows - Menú interactivo
rollback.bat
```

### Verificar Estado

```bash
# Linux/Mac
./rollback.sh --status

# Windows
rollback.bat
# Seleccionar opción 6
```

## Configuración Rápida

### Variables de Entorno (.env.production)

```bash
# Rollback
ROLLBACK_ENABLED=true
AUTO_ROLLBACK=true
HEALTH_CHECK_RETRIES=3
HEALTH_CHECK_DELAY=10

# Notificaciones (opcional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
NOTIFICATION_EMAIL=admin@example.com
```

## Escenarios Comunes

### 1. Despliegue Falló - Rollback Automático

**Qué hace el sistema:**
- ✅ Detecta el error automáticamente
- ✅ Revierte el código
- ✅ Restaura la base de datos
- ✅ Reinicia servicios
- ✅ Envía notificación

**Acción requerida:** Ninguna (automático)

### 2. Necesito Revertir Manualmente

```bash
# Opción 1: Rollback rápido
./rollback.sh --quick

# Opción 2: Rollback a commit específico
./rollback.sh --commit abc123

# Opción 3: Menú interactivo
./rollback.sh
```

### 3. Solo Necesito Restaurar la Base de Datos

```bash
# Ver backups disponibles
ls -lh backups/

# Restaurar backup específico
./rollback.sh --backup backups/backup_20250109_120000.sql.gz
```

### 4. Verificar que Todo Funciona

```bash
# Verificar servicios
docker-compose -f docker-compose.prod.yml ps

# Verificar health check
curl http://localhost/health/

# O usar el script
./rollback.sh --status
```

## Ubicaciones Importantes

### Backups
```
/app/backups/
├── backup_20250109_120000.sql.gz  ← Backups automáticos
├── backup_20250109_140000.sql.gz
└── safety_backup_20250109_150000.sql.gz  ← Backups de seguridad
```

### Logs
```
/app/logs/
├── update.log          ← Log de actualizaciones
├── rollback.log        ← Log de rollbacks
└── notifications.log   ← Log de notificaciones
```

## Troubleshooting Rápido

### Problema: Rollback Automático Falló

```bash
# 1. Ver logs
tail -f logs/rollback.log

# 2. Verificar servicios
docker-compose -f docker-compose.prod.yml ps

# 3. Intentar rollback manual
./rollback.sh --quick
```

### Problema: Base de Datos No Se Restaura

```bash
# 1. Verificar que el backup existe
ls -lh backups/

# 2. Verificar integridad
gunzip -t backups/backup_20250109_120000.sql.gz

# 3. Restaurar manualmente
gunzip -c backups/backup_20250109_120000.sql.gz | \
  docker-compose -f docker-compose.prod.yml exec -T db \
  psql -U certificados_user certificados_prod
```

### Problema: Servicios No Inician

```bash
# 1. Ver logs de Docker
docker-compose -f docker-compose.prod.yml logs

# 2. Reconstruir imágenes
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# 3. Verificar configuración
docker-compose -f docker-compose.prod.yml config
```

## Notificaciones

### Tipos de Notificaciones

| Tipo | Significado | Acción |
|------|-------------|--------|
| INFO | Inicio de actualización | Ninguna |
| SUCCESS | Actualización exitosa | Ninguna |
| WARNING | Actualización con advertencias | Revisar logs |
| ERROR | Error durante actualización | Revisar logs |
| ROLLBACK_SUCCESS | Rollback exitoso | Revisar causa |
| ROLLBACK_FAILED | Rollback falló | **Intervención inmediata** |

### Configurar Slack

1. Crear webhook en Slack
2. Agregar a `.env.production`:
   ```bash
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
   ```
3. Reiniciar servicios

## Mejores Prácticas

✅ **Siempre probar en staging primero**
✅ **Verificar backups regularmente**
✅ **Monitorear notificaciones**
✅ **Mantener logs organizados**
✅ **Documentar cambios críticos**

## Comandos de Emergencia

### Detener Todo
```bash
docker-compose -f docker-compose.prod.yml down
```

### Reiniciar Todo
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Ver Logs en Tiempo Real
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### Backup Manual de Emergencia
```bash
docker-compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U certificados_user certificados_prod > emergency_backup.sql
gzip emergency_backup.sql
```

## Contacto de Emergencia

En caso de problemas críticos:
1. Revisar logs: `tail -f logs/*.log`
2. Verificar servicios: `docker-compose ps`
3. Intentar rollback: `./rollback.sh --quick`
4. Si todo falla: Contactar al equipo de desarrollo

## Documentación Completa

Para más detalles, consultar:
- `docs/ROLLBACK_SYSTEM.md` - Documentación completa
- `TASK_9_ROLLBACK_SUMMARY.md` - Resumen de implementación
- `update-production.sh` - Script de actualización
- `rollback.sh` - Script de rollback

---

**Última actualización:** 2025-01-09
**Versión:** 1.0
