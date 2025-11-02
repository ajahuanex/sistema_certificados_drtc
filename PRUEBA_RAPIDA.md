# 🧪 Guía de Prueba Rápida - Sistema de Certificados

## ✅ Servidor Levantado

El servidor está corriendo en: **http://localhost:8000**

---

## 🎯 Qué Probar (en orden)

### 1️⃣ Dashboard de Estadísticas ⭐ NUEVO

**URL:** http://localhost:8000/admin/dashboard/

**Qué verás:**
- 📊 Estadísticas generales (total de certificados, eventos, participantes)
- 📈 Gráficos de certificados por mes
- 📋 Últimas consultas de DNI
- 🔍 Últimas verificaciones de QR

**Prueba:**
- Ver las métricas
- Hacer clic en "Actualizar Datos"
- Explorar los gráficos

---

### 2️⃣ Consulta de Certificados (con botón de FirmaPerú) ⭐ NUEVO

**URL:** http://localhost:8000/consulta/

**Qué verás:**
- Formulario de búsqueda por DNI (sin placeholder ahora)
- Tabla de resultados moderna
- **Botón verde "Firma"** en certificados firmados ⭐ NUEVO

**Prueba:**
1. Buscar un DNI existente
2. Ver la tabla de resultados
3. Hacer clic en el botón "Firma" (abre FirmaPerú)
4. Descargar un certificado

---

### 3️⃣ Importar PDFs con QR ⭐ NUEVO

**URL:** http://localhost:8000/admin/pdf-import/

**Qué verás:**
- Formulario con drag & drop
- Selector de evento
- Opción de extracción automática de nombres

**Prueba:**
1. Seleccionar un evento
2. Arrastrar algunos PDFs de prueba
3. Ver la lista de archivos seleccionados
4. Importar

**Nota:** Necesitas PDFs de prueba para esto.

---

### 4️⃣ Procesar QR en Certificados ⭐ NUEVO

**URL:** http://localhost:8000/admin/certificates/certificate/

**Qué hacer:**
1. Filtrar certificados por estado: "IMPORTED"
2. Seleccionar algunos certificados
3. En "Acción": Seleccionar "🔄 Procesar QR"
4. Hacer clic en "Ir"

**Resultado:**
- Se genera QR con URL de preview
- Se inserta QR en el PDF
- Estado cambia a "QR_INSERTED"

---

### 5️⃣ Exportar para Firma ⭐ NUEVO

**URL:** http://localhost:8000/admin/certificates/certificate/

**Qué hacer:**
1. Filtrar por estado: "QR_INSERTED"
2. Seleccionar certificados
3. En "Acción": Seleccionar "📤 Exportar para firma digital"
4. Hacer clic en "Ir"

**Resultado:**
- Se descarga un ZIP con:
  - PDFs con QR
  - metadata.csv

---

### 6️⃣ Vista de Verificación (con botón FirmaPerú) ⭐ NUEVO

**URL:** http://localhost:8000/verificar/{uuid}/

**Qué verás:**
- Información completa del certificado
- **Botón verde "Verificar Firma Digital"** ⭐ NUEVO
- Botón de descarga

**Prueba:**
1. Buscar un certificado por DNI
2. Hacer clic en "QR" para verificar
3. Ver el botón de verificación de firma
4. Hacer clic (abre FirmaPerú)

---

### 7️⃣ Preview Público ⭐ NUEVO

**URL:** http://localhost:8000/certificado/{uuid}/preview/

**Qué verás:**
- Diseño moderno con gradiente
- Badge de "Certificado Auténtico"
- Información de verificación
- Visor de PDF embebido
- **Botón "Verificar Firma Digital"** ⭐ NUEVO
- Código QR visible

**Prueba:**
1. Acceder con el UUID de un certificado firmado
2. Ver el diseño completo
3. Probar el botón de verificación de firma
4. Descargar el PDF

---

## 🎨 Nuevas Funcionalidades a Probar

### ✅ Sistema de QR Completo:
- [x] Importar PDFs originales
- [x] Procesar QR automáticamente
- [x] Exportar para firma
- [x] Importar certificados firmados
- [x] Preview público elegante

### ✅ Dashboard de Estadísticas:
- [x] Métricas generales
- [x] Gráficos interactivos
- [x] Últimas actividades
- [x] Botón de actualización

### ✅ Verificación de Firma Digital:
- [x] Botón en preview público
- [x] Botón en verificación
- [x] Botón en tabla de resultados
- [x] Integración con FirmaPerú

---

## 🔗 URLs Importantes

```
Admin Principal:
http://localhost:8000/admin/

Dashboard (NUEVO):
http://localhost:8000/admin/dashboard/

Importar PDFs (NUEVO):
http://localhost:8000/admin/pdf-import/

Importar Finales (NUEVO):
http://localhost:8000/admin/final-import/

Consulta Pública:
http://localhost:8000/consulta/

Certificados Admin:
http://localhost:8000/admin/certificates/certificate/

Configuración QR (NUEVO):
http://localhost:8000/admin/certificates/qrprocessingconfig/
```

---

## 🎯 Flujo de Prueba Completo

### Escenario 1: Certificado Normal
```
1. Ir a Dashboard → Ver estadísticas
2. Ir a Consulta → Buscar por DNI
3. Ver tabla con botón "Firma"
4. Hacer clic en "QR" → Ver verificación
5. Hacer clic en "Verificar Firma Digital"
```

### Escenario 2: Procesamiento con QR (si tienes PDFs)
```
1. Ir a Importar PDFs
2. Seleccionar evento
3. Subir PDFs
4. Ir a Admin de Certificados
5. Procesar QR
6. Exportar ZIP
7. Importar finales (simulando firma)
8. Ver preview público
```

---

## 📸 Qué Buscar

### Dashboard:
- ✅ Números grandes con estadísticas
- ✅ Gráfico de barras por mes
- ✅ Tabla de últimas consultas
- ✅ Botón "Actualizar Datos"

### Consulta:
- ✅ Campo DNI sin placeholder
- ✅ Tabla moderna tipo DataTable
- ✅ Botón verde "Firma" en certificados firmados
- ✅ Botones de acción compactos

### Preview Público:
- ✅ Diseño con gradiente morado
- ✅ Badge verde de autenticidad
- ✅ Información en tarjetas
- ✅ Visor de PDF
- ✅ Botón verde "Verificar Firma Digital"

---

## 🐛 Si Algo No Funciona

### Error 404 en alguna URL:
```bash
# Verificar URLs
python manage.py show_urls
```

### Error en templates:
```bash
# Verificar que los templates existen
dir templates\certificates\
dir templates\admin\certificates\
```

### Error de base de datos:
```bash
# Verificar migraciones
python manage.py showmigrations
```

---

## ✨ Características Nuevas Visibles

1. **Dashboard completo** con gráficos
2. **Botón de verificación de firma** en 3 lugares
3. **Sistema de QR** con importación/exportación
4. **Preview público** con diseño moderno
5. **Campo DNI** sin placeholder

---

## 🎉 ¡Disfruta Probando!

El sistema tiene muchas mejoras nuevas. Explora cada sección y verás:
- Mejor diseño
- Más funcionalidades
- Mejor experiencia de usuario

**¿Alguna pregunta mientras pruebas?** 🚀
