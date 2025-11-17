# ⚡ Pruebas Locales - Guía Rápida

## 🚀 Inicio Rápido

### 1. Ejecutar Pruebas Automatizadas

**Opción A - Script Batch (Recomendado para Windows):**
```cmd
test-local-completo.bat
```

**Opción B - PowerShell (Más detallado):**
```powershell
.\test-local-completo.ps1
```

---

## 🌐 URLs Principales

| Función | URL | Credenciales |
|---------|-----|--------------|
| **Admin** | http://localhost:7070/admin/ | admin / admin123 |
| **Dashboard** | http://localhost:7070/admin/dashboard/ | (requiere login) |
| **Consulta Pública** | http://localhost:7070/consulta/ | - |
| **Verificar Certificado** | http://localhost:7070/verificar/{uuid}/ | - |

---

## 🧪 Pruebas Manuales Rápidas

### ✅ Prueba 1: Login Admin (30 segundos)
1. Abre: http://localhost:7070/admin/
2. Usuario: `admin` / Contraseña: `admin123`
3. ✅ Deberías ver el panel de administración

### ✅ Prueba 2: Dashboard (30 segundos)
1. Ve a: http://localhost:7070/admin/dashboard/
2. ✅ Deberías ver estadísticas y gráficos

### ✅ Prueba 3: Consulta Certificado (1 minuto)
1. Abre: http://localhost:7070/consulta/
2. Ingresa DNI: `99238323`
3. Click en "Buscar"
4. ✅ Deberías ver el certificado en la tabla
5. Click en "Descargar PDF"
6. ✅ Debería descargar el PDF

### ✅ Prueba 4: Verificar Certificado (30 segundos)
1. Abre: http://localhost:7070/verificar/9f446c3e-6acc-4ba9-a49d-8a998a331f89/
2. ✅ Deberías ver los detalles del certificado con QR

### ✅ Prueba 5: Generar Certificados (1 minuto)
1. Ve a: http://localhost:7070/admin/certificates/evento/
2. Selecciona un evento (checkbox)
3. Acción: "Generar certificados para participantes"
4. Click "Ir"
5. ✅ Mensaje de éxito

---

## 🔧 Comandos Útiles

### Verificar Servidor
```powershell
# PowerShell
Invoke-WebRequest -Uri "http://localhost:7070/admin/" -Method Head

# O simplemente abre el navegador
start http://localhost:7070/admin/
```

### Ver Procesos
```cmd
# Ver si Python está corriendo
tasklist | findstr python

# Ver puerto 7070
netstat -ano | findstr :7070
```

### Reiniciar Servidor
```cmd
# Detener
taskkill /F /IM python.exe

# Iniciar
python manage.py runserver 7070
```

---

## 📊 DNIs de Prueba

| DNI | Nombre | Tiene Certificado |
|-----|--------|-------------------|
| 99238323 | Juan Morales Rodríguez | ✅ Sí |
| 88459901 | María Díaz Rodríguez | ✅ Sí |
| 71257548 | Carmen Gómez Jiménez | ✅ Sí |
| 81925349 | Lucía Navarro Serrano | ✅ Sí |
| 87140676 | Carlos Moreno Morales | ✅ Sí |

---

## ⚠️ Problemas Comunes

### Problema: "curl: The term 'curl' is not recognized"
**Solución:** Estás en PowerShell, usa:
```powershell
Invoke-WebRequest -Uri "http://localhost:7070/admin/"
```

### Problema: No puedo acceder al admin
**Solución:**
```cmd
python manage.py create_superuser_if_not_exists --update --noinput
```

### Problema: Archivos estáticos no cargan
**Solución:**
```cmd
python manage.py collectstatic --noinput
```

### Problema: Puerto ocupado
**Solución:** Usa otro puerto:
```cmd
python manage.py runserver 8000
```

---

## ✅ Checklist Rápido

Marca lo que ya probaste:

- [ ] Servidor corriendo en http://localhost:7070
- [ ] Login admin funciona
- [ ] Dashboard muestra estadísticas
- [ ] Consulta pública funciona
- [ ] Descarga de PDF funciona
- [ ] Verificación de certificado funciona
- [ ] Archivos estáticos cargan correctamente
- [ ] No hay errores en consola del navegador (F12)

---

## 🎯 Resultado Esperado

Si todas las pruebas pasan:
- ✅ Sistema funcionando correctamente en local
- ✅ Listo para pruebas de producción con Docker
- ✅ Listo para despliegue en servidor

---

## 📝 Siguiente Paso

Una vez completadas las pruebas locales:

1. **Pruebas con Docker local:**
   ```cmd
   test-produccion-local.bat
   ```

2. **Despliegue en Ubuntu:**
   ```bash
   ./deploy-ubuntu.sh
   ```

3. **Revisar guía completa:**
   - GUIA_PRUEBAS_LOCALES.md
   - GUIA_DESPLIEGUE_PRODUCCION_2025.md

---

## 💡 Tips

- Usa **modo incógnito** (Ctrl + Shift + N) para evitar caché
- Mantén **F12** abierto para ver errores de JavaScript
- Revisa **logs/django.log** si algo falla
- Usa **Postman** para probar APIs

---

**Tiempo estimado total:** 5-10 minutos

¡Buena suerte! 🚀
