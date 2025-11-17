# 🧪 Guía Completa de Pruebas Locales

## Estado Actual
Servidor corriendo en: **http://localhost:7070**

---

## ✅ Checklist de Pruebas

### 1️⃣ Verificar que el Servidor Está Corriendo

**Comando PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://localhost:7070/admin/" -Method Head
```

**O simplemente abre tu navegador:**
```
http://localhost:7070/admin/
```

**Resultado esperado:** Deberías ver la página de login de Django Admin

---

### 2️⃣ Iniciar Sesión en el Admin

**URL:** http://localhost:7070/admin/

**Credenciales:**
- Usuario: `admin`
- Contraseña: `admin123`

**Qué verificar:**
- ✅ Login exitoso
- ✅ Ves el panel de administración de Django
- ✅ Ves los modelos: Eventos, Participantes, Certificados, etc.

---

### 3️⃣ Probar el Dashboard

**URL:** http://localhost:7070/admin/dashboard/

**Qué verificar:**
- ✅ Estadísticas generales (eventos, participantes, certificados)
- ✅ Gráficos de certificados por mes
- ✅ Tabla de eventos recientes
- ✅ Logs de actividad reciente

---

### 4️⃣ Consulta Pública de Certificados

**URL:** http://localhost:7070/consulta/

**DNIs de prueba con certificados:**
- 99238323
- 88459901
- 71257548
- 81925349
- 87140676

**Qué verificar:**
- ✅ Formulario de búsqueda funciona
- ✅ Muestra resultados con DataTable
- ✅ Botón de descarga funciona
- ✅ Botón de verificación funciona

---

### 5️⃣ Verificar Certificado por UUID

**URL de ejemplo:**
```
http://localhost:7070/verificar/9f446c3e-6acc-4ba9-a49d-8a998a331f89/
```

**Qué verificar:**
- ✅ Muestra información del certificado
- ✅ Muestra código QR
- ✅ Muestra estado de firma digital
- ✅ Diseño responsive

---

### 6️⃣ Descargar Certificado PDF

**Desde la consulta:**
1. Busca DNI: 99238323
2. Click en "Descargar PDF"

**Qué verificar:**
- ✅ Descarga el archivo PDF
- ✅ El PDF se abre correctamente
- ✅ Contiene código QR
- ✅ Datos del participante correctos

---

### 7️⃣ Generar Certificados desde Admin

**Pasos:**
1. Ve a: http://localhost:7070/admin/certificates/evento/
2. Selecciona un evento (checkbox)
3. En "Acción" selecciona "Generar certificados para participantes"
4. Click en "Ir"

**Qué verificar:**
- ✅ Mensaje de éxito
- ✅ Certificados generados
- ✅ Logs de auditoría creados

---

### 8️⃣ Importar Excel

**URL:** http://localhost:7070/admin/import-excel/

**Archivo de prueba:** Crea un Excel con estas columnas:
```
evento_nombre | participante_nombre | participante_dni | participante_email
```

**Qué verificar:**
- ✅ Formulario de carga funciona
- ✅ Validación de formato
- ✅ Importación exitosa
- ✅ Participantes creados

---

### 9️⃣ Editor de Plantillas

**URL:** http://localhost:7070/admin/certificates/certificatetemplate/

**Qué verificar:**
- ✅ Lista de plantillas
- ✅ Botón "Editar en Editor Visual"
- ✅ Editor se abre correctamente
- ✅ Previsualización funciona

---

### 🔟 Archivos Estáticos

**URLs a probar:**
```
http://localhost:7070/static/admin/css/base.css
http://localhost:7070/static/admin/js/dashboard.js
http://localhost:7070/static/admin/css/dashboard.css
```

**Qué verificar:**
- ✅ Archivos CSS se cargan
- ✅ Archivos JS se cargan
- ✅ No hay errores 404

---

## 🔧 Comandos Útiles para Pruebas

### Verificar Estado del Servidor
```powershell
# Ver procesos de Python
Get-Process python

# Verificar puerto 7070
netstat -ano | findstr :7070
```

### Reiniciar Servidor
```powershell
# Detener servidor
taskkill /F /IM python.exe

# Iniciar servidor
python manage.py runserver 7070
```

### Ver Logs en Tiempo Real
```powershell
# En otra terminal
Get-Content logs\django.log -Wait -Tail 50
```

### Ejecutar Tests
```powershell
# Todos los tests
python manage.py test

# Tests específicos
python manage.py test certificates.tests.test_views
python manage.py test certificates.tests.test_admin
```

---

## 🐛 Troubleshooting

### Problema: No puedo acceder al admin
**Solución:**
```powershell
# Recrear superusuario
python manage.py create_superuser_if_not_exists --update --noinput
```

### Problema: Archivos estáticos no cargan
**Solución:**
```powershell
# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

### Problema: Error de base de datos
**Solución:**
```powershell
# Aplicar migraciones
python manage.py migrate
```

### Problema: Puerto 7070 ocupado
**Solución:**
```powershell
# Usar otro puerto
python manage.py runserver 8000
```

---

## 📊 Resultados Esperados

Al completar todas las pruebas, deberías tener:

- ✅ Admin funcionando correctamente
- ✅ Dashboard con estadísticas
- ✅ Consulta pública operativa
- ✅ Descarga de PDFs funcional
- ✅ Verificación de certificados OK
- ✅ Generación de certificados OK
- ✅ Importación de Excel OK
- ✅ Editor de plantillas OK
- ✅ Archivos estáticos cargando
- ✅ Sin errores en consola

---

## 📝 Reporte de Pruebas

Usa esta plantilla para documentar tus pruebas:

```
FECHA: [fecha]
HORA: [hora]
TESTER: [tu nombre]

PRUEBAS REALIZADAS:
[ ] 1. Servidor corriendo
[ ] 2. Login admin
[ ] 3. Dashboard
[ ] 4. Consulta pública
[ ] 5. Verificación UUID
[ ] 6. Descarga PDF
[ ] 7. Generar certificados
[ ] 8. Importar Excel
[ ] 9. Editor plantillas
[ ] 10. Archivos estáticos

ERRORES ENCONTRADOS:
- [Descripción del error]

NOTAS ADICIONALES:
- [Observaciones]
```

---

## 🚀 Siguiente Paso

Una vez completadas todas las pruebas locales exitosamente, estarás listo para:

1. **Despliegue en Docker local** (test-produccion-local.bat)
2. **Despliegue en servidor Ubuntu** (deploy-ubuntu.sh)
3. **Configuración de dominio y SSL**

---

## 💡 Tips

- Usa **modo incógnito** en el navegador para evitar problemas de caché
- Mantén la **consola de desarrollador** abierta (F12) para ver errores
- Revisa los **logs** en `logs/django.log` si algo falla
- Usa **Postman** o **curl** para probar APIs si es necesario

---

¡Buena suerte con las pruebas! 🎉
