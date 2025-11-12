# ✅ Checklist de Despliegue a Producción

## 📋 Pre-requisitos

- [ ] Docker Desktop instalado y corriendo
- [ ] Archivo `.env.production` configurado
- [ ] Terminal CMD abierta en la carpeta del proyecto

---

## 🚀 Pasos de Despliegue

### 1️⃣ Limpiar Ambiente Anterior
```cmd
docker-compose -f docker-compose.prod.yml down
```
- [ ] Ejecutado sin errores

### 2️⃣ Reconstruir Imagen
```cmd
docker-compose -f docker-compose.prod.yml build --no-cache web
```
- [ ] Construcción completada
- [ ] Sin errores en la salida

### 3️⃣ Iniciar Servicios
```cmd
docker-compose -f docker-compose.prod.yml up -d
```
- [ ] Todos los servicios iniciados
- [ ] Sin errores en la salida

### 4️⃣ Verificar Estado
```cmd
docker-compose -f docker-compose.prod.yml ps
```
- [ ] `certificados_db_prod` → Up (healthy)
- [ ] `certificados_redis_prod` → Up (healthy)
- [ ] `certificados_web_prod` → Up
- [ ] `certificados_nginx_prod` → Up

### 5️⃣ Verificar Logs
```cmd
docker-compose -f docker-compose.prod.yml logs web --tail=50
```
- [ ] Sin errores críticos
- [ ] Mensaje "Iniciando aplicación..." visible
- [ ] Gunicorn iniciado correctamente

### 6️⃣ Verificar Health Check
```cmd
curl http://localhost/health/
```
O abrir en navegador: http://localhost/health/

- [ ] Responde con status "healthy"
- [ ] Todos los servicios reportan "healthy"

---

## 🌐 Verificación de Acceso

### Página Principal
- [ ] http://localhost/ carga correctamente
- [ ] Sin errores 500 o 404
- [ ] Estilos CSS cargados

### Panel de Administración
- [ ] http://localhost/admin/ carga correctamente
- [ ] Formulario de login visible
- [ ] Puedes iniciar sesión con credenciales de admin

### API
- [ ] http://localhost/api/ responde
- [ ] Documentación de API visible (si está configurada)

---

## 🔍 Verificación de Servicios

### PostgreSQL
```cmd
docker-compose -f docker-compose.prod.yml exec db psql -U certificados_user -d certificados_prod -c "\dt"
```
- [ ] Conexión exitosa
- [ ] Tablas de Django visibles

### Redis
```cmd
docker-compose -f docker-compose.prod.yml exec redis redis-cli PING
```
- [ ] Responde "PONG"

### Archivos Estáticos
- [ ] CSS cargando correctamente
- [ ] JavaScript funcionando
- [ ] Imágenes visibles

### Archivos Media
- [ ] Directorio `/media` accesible
- [ ] Subida de archivos funciona

---

## 📊 Monitoreo Inicial

### Ver Logs en Tiempo Real
```cmd
docker-compose -f docker-compose.prod.yml logs -f
```
- [ ] Logs fluyendo sin errores
- [ ] Sin warnings críticos

### Ver Uso de Recursos
```cmd
docker stats
```
- [ ] CPU < 80%
- [ ] Memoria < 80%
- [ ] Sin contenedores reiniciándose

---

## 🔐 Seguridad

- [ ] `DEBUG=False` en `.env.production`
- [ ] `SECRET_KEY` único y seguro (no el de ejemplo)
- [ ] Contraseña de DB segura
- [ ] Contraseña de admin segura
- [ ] `ALLOWED_HOSTS` configurado correctamente

---

## 💾 Backup

### Crear Backup Inicial
```cmd
docker-compose -f docker-compose.prod.yml exec db pg_dump -U certificados_user certificados_prod > backup_inicial.sql
```
- [ ] Backup creado exitosamente
- [ ] Archivo `backup_inicial.sql` existe

---

## 📝 Documentación

- [ ] Credenciales de admin documentadas (en lugar seguro)
- [ ] URL de acceso documentada
- [ ] Procedimientos de backup documentados
- [ ] Contactos de soporte documentados

---

## 🎯 Pruebas Funcionales

### Funcionalidad Básica
- [ ] Crear evento
- [ ] Importar participantes desde Excel
- [ ] Generar certificados
- [ ] Descargar certificado PDF
- [ ] Verificar certificado por QR
- [ ] Buscar certificado por DNI

### Funcionalidad Admin
- [ ] Acceso al panel de admin
- [ ] Ver lista de eventos
- [ ] Ver lista de participantes
- [ ] Ver lista de certificados
- [ ] Editar plantilla de certificado

---

## 🚨 Plan de Contingencia

### Si algo falla:

1. **Ver logs detallados:**
   ```cmd
   docker-compose -f docker-compose.prod.yml logs --tail=200
   ```

2. **Reiniciar servicios:**
   ```cmd
   docker-compose -f docker-compose.prod.yml restart
   ```

3. **Reconstruir desde cero:**
   ```cmd
   docker-compose -f docker-compose.prod.yml down -v
   docker-compose -f docker-compose.prod.yml build --no-cache
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Consultar documentación:**
   - `DESPLIEGUE_PRODUCCION_COMPLETO.md`
   - `SOLUCION_RAPIDA_PRODUCCION.md`
   - `COMANDOS_RAPIDOS_PRODUCCION.md`

---

## ✅ Despliegue Completado

Una vez que todos los items estén marcados:

- [ ] **Todos los servicios corriendo**
- [ ] **Health checks pasando**
- [ ] **Acceso web funcionando**
- [ ] **Funcionalidad básica verificada**
- [ ] **Backup inicial creado**
- [ ] **Documentación actualizada**

---

## 🎉 ¡Producción Lista!

Tu aplicación está ahora en producción y lista para usar.

**Próximos pasos:**
1. Configurar backups automáticos
2. Configurar monitoreo
3. Configurar SSL/HTTPS (opcional)
4. Configurar dominio personalizado (opcional)

**Comandos útiles para el día a día:**
```cmd
REM Ver estado
docker-compose -f docker-compose.prod.yml ps

REM Ver logs
docker-compose -f docker-compose.prod.yml logs -f

REM Reiniciar
docker-compose -f docker-compose.prod.yml restart

REM Detener
docker-compose -f docker-compose.prod.yml stop

REM Iniciar
docker-compose -f docker-compose.prod.yml start
```

---

**Fecha de despliegue:** _______________  
**Desplegado por:** _______________  
**Versión:** _______________  
**Notas:** _______________
