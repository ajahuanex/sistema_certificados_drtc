# 🎯 Cómo Usar el Sistema de Procesamiento de Certificados con QR

## 📋 Guía Paso a Paso

### ✅ Requisitos Previos

1. **Configuración inicial creada:**
```bash
python manage.py load_qr_config
```

2. **Servidor corriendo:**
```bash
python manage.py runserver
```

3. **Usuario administrador creado**

---

## 🔄 Flujo Completo

### 1️⃣ IMPORTAR CERTIFICADOS PDF ORIGINALES

**Acceso:** `http://localhost:8000/admin/pdf-import/`

**Pasos:**
1. Hacer clic en "Importar PDFs" en el menú del admin
2. Seleccionar el evento al que pertenecen los certificados
3. Arrastrar y soltar los archivos PDF (o hacer clic para seleccionar)
4. Verificar que la opción "Extraer nombres automáticamente" esté marcada
5. Hacer clic en "Importar Certificados"

**Resultado:**
- ✅ Se crean certificados en estado `IMPORTED`
- ✅ Se extraen nombres automáticamente de los PDFs
- ✅ Se crean participantes si no existen

**Ejemplo de nombres de archivo:**
```
JUAN_PEREZ_GARCIA.pdf
MARIA_LOPEZ_RODRIGUEZ.pdf
CARLOS_SANCHEZ_TORRES.pdf
```

---

### 2️⃣ PROCESAR CÓDIGOS QR

**Acceso:** Admin de Django → Certificados

**Pasos:**
1. Ir a: `http://localhost:8000/admin/certificates/certificate/`
2. Filtrar por "Estado de Procesamiento": `IMPORTED`
3. Seleccionar los certificados que deseas procesar
4. En "Acción": Seleccionar "🔄 Procesar QR para certificados seleccionados"
5. Hacer clic en "Ir"

**Resultado:**
- ✅ Se genera código QR con URL de preview
- ✅ Se inserta QR en el PDF original
- ✅ Estado cambia a `QR_INSERTED`
- ✅ Se crea archivo `qr_pdf` listo para firma

**Tiempo estimado:** ~5 segundos por certificado

---

### 3️⃣ EXPORTAR PARA FIRMA DIGITAL

**Acceso:** Admin de Django → Certificados

**Pasos:**
1. Filtrar por "Estado de Procesamiento": `QR_INSERTED`
2. Seleccionar los certificados a exportar
3. En "Acción": Seleccionar "📤 Exportar para firma digital"
4. Hacer clic en "Ir"
5. Se descarga automáticamente un archivo ZIP

**Contenido del ZIP:**
```
certificados_export_20250131_143022.zip
├── 123e4567-e89b-12d3-a456-426614174000_12345678.pdf
├── 234e5678-e89b-12d3-a456-426614174001_23456789.pdf
├── 345e6789-e89b-12d3-a456-426614174002_34567890.pdf
└── metadata.csv
```

**metadata.csv contiene:**
```csv
UUID,DNI,Nombre,Evento,Fecha_Exportacion
123e4567-e89b-12d3-a456-426614174000,12345678,JUAN PEREZ GARCIA,Capacitación 2024,2025-01-31 14:30:22
```

**Resultado:**
- ✅ Estado cambia a `EXPORTED_FOR_SIGNING`
- ✅ Se registra fecha de exportación

---

### 4️⃣ FIRMAR CERTIFICADOS (EXTERNO)

**Herramientas sugeridas:**
- Adobe Acrobat Pro
- DocuSign
- Firma Digital RENIEC
- Cualquier herramienta de firma digital

**IMPORTANTE:**
- ⚠️ **NO cambiar los nombres de los archivos**
- ⚠️ Los archivos deben mantener el UUID en el nombre
- ⚠️ Ejemplo: `123e4567-e89b-12d3-a456-426614174000_12345678.pdf`

**Pasos:**
1. Extraer archivos del ZIP
2. Firmar cada PDF con tu herramienta de firma digital
3. Guardar los PDFs firmados manteniendo los nombres originales

---

### 5️⃣ IMPORTAR CERTIFICADOS FIRMADOS

**Acceso:** `http://localhost:8000/admin/final-import/`

**Pasos:**
1. Hacer clic en "Importar Certificados Firmados" en el menú
2. Arrastrar y soltar los PDFs firmados (o hacer clic para seleccionar)
3. Verificar que los archivos tengan el ✓ verde (indica UUID válido)
4. Hacer clic en "Importar Certificados Firmados"

**Resultado:**
- ✅ Sistema identifica certificados por UUID
- ✅ Estado cambia a `SIGNED_FINAL`
- ✅ Certificados listos para preview público
- ✅ Se registra fecha de importación final

---

### 6️⃣ VERIFICAR PREVIEW PÚBLICO

**Acceso:** Escanear QR o URL directa

**Opciones de acceso:**
1. **Escanear QR del certificado** (recomendado)
2. **URL directa:** `http://localhost:8000/certificado/{UUID}/preview/`

**Ejemplo:**
```
http://localhost:8000/certificado/123e4567-e89b-12d3-a456-426614174000/preview/
```

**Qué verás:**
- ✅ Badge de "Certificado Auténtico y Verificado"
- ✅ Información completa del participante
- ✅ Visor de PDF embebido
- ✅ Código QR visible
- ✅ Botón de descarga
- ✅ Diseño responsive (funciona en móvil)

---

## 🎨 Personalización

### Cambiar Posición del QR

**Acceso:** Admin → QR Processing Config

1. Ir a: `http://localhost:8000/admin/certificates/qrprocessingconfig/`
2. Editar la configuración activa
3. Cambiar valores:
   - **Posición X por Defecto:** Píxeles desde la izquierda (default: 450)
   - **Posición Y por Defecto:** Píxeles desde arriba (default: 50)
   - **Tamaño por Defecto:** Tamaño del QR en píxeles (default: 100)
4. Guardar

**Ejemplo de posiciones:**
```
Esquina superior derecha: X=450, Y=50
Esquina inferior derecha: X=450, Y=700
Esquina inferior izquierda: X=50, Y=700
Centro: X=250, Y=400
```

### Cambiar URL Base para QR

1. Editar configuración activa
2. Cambiar **URL Base para Preview**
3. Ejemplo: `https://certificados.drtcpuno.gob.pe`
4. Guardar

**Importante:** Los QR ya generados mantendrán la URL anterior. Solo afecta a nuevos QR.

### Cambiar Tamaño Máximo de PDF

1. Editar configuración activa
2. Cambiar **Tamaño Máximo de PDF (MB)**
3. Default: 10 MB
4. Guardar

---

## 📊 Monitoreo y Estado

### Ver Estado de Procesamiento

**Acceso:** `http://localhost:8000/admin/processing-status/`

**Información disponible:**
- Total de certificados
- Certificados por estado
- Últimos certificados procesados
- Errores recientes

### Filtrar Certificados por Estado

En el admin de certificados:
1. Usar el filtro "Estado de Procesamiento"
2. Opciones:
   - `IMPORTED` - Importados, listos para procesar QR
   - `QR_INSERTED` - Con QR, listos para exportar
   - `EXPORTED_FOR_SIGNING` - Exportados, esperando firma
   - `SIGNED_FINAL` - Firmados, disponibles públicamente
   - `ERROR` - Con errores de procesamiento

---

## 🔍 Solución de Problemas

### Problema: "No se pudo extraer nombre del PDF"

**Solución:**
- Verificar que el nombre del archivo tenga al menos 2 palabras
- O que el PDF contenga texto con el nombre del participante
- Alternativamente, desmarcar "Extraer nombres automáticamente" y mapear manualmente

### Problema: "QR no es legible"

**Solución:**
- Verificar configuración de calidad del QR
- Aumentar el tamaño del QR
- Cambiar nivel de corrección de errores a 'H' (High)

### Problema: "Certificado no encontrado al importar final"

**Solución:**
- Verificar que el nombre del archivo contenga el UUID
- Verificar que el certificado esté en estado `EXPORTED_FOR_SIGNING`
- Revisar el archivo metadata.csv del ZIP exportado

### Problema: "Preview muestra 'Certificado No Disponible'"

**Solución:**
- Verificar que el certificado esté en estado `SIGNED_FINAL`
- Verificar que el archivo `final_pdf` exista
- Revisar logs de errores

---

## 📝 Buenas Prácticas

### Nomenclatura de Archivos

**Para importación inicial:**
```
✅ JUAN_PEREZ_GARCIA.pdf
✅ Maria Lopez Rodriguez.pdf
✅ carlos-sanchez-torres.pdf
❌ certificado1.pdf (muy genérico)
❌ doc.pdf (sin información)
```

### Organización de Eventos

- Crear un evento por cada capacitación/curso
- Usar nombres descriptivos
- Incluir fecha en el nombre del evento

### Procesamiento en Lotes

- Procesar certificados en lotes de 50-100 para mejor rendimiento
- Exportar por evento para mejor organización
- Mantener respaldos de los ZIP exportados

### Seguridad

- Solo usuarios staff pueden acceder a funciones de procesamiento
- Los preview públicos tienen rate limiting (30 req/min)
- Todos los accesos se registran en auditoría

---

## 🎯 Atajos Rápidos

### URLs Importantes

```
Admin Principal:
http://localhost:8000/admin/

Importar PDFs:
http://localhost:8000/admin/pdf-import/

Importar Finales:
http://localhost:8000/admin/final-import/

Estado de Procesamiento:
http://localhost:8000/admin/processing-status/

Certificados:
http://localhost:8000/admin/certificates/certificate/

Configuración QR:
http://localhost:8000/admin/certificates/qrprocessingconfig/
```

### Comandos Útiles

```bash
# Crear configuración inicial
python manage.py load_qr_config

# Ver configuración activa
python manage.py shell
>>> from certificates.models import QRProcessingConfig
>>> config = QRProcessingConfig.get_active_config()
>>> print(f"Posición: ({config.default_qr_x}, {config.default_qr_y})")
>>> print(f"Tamaño: {config.default_qr_size}px")
>>> print(f"URL: {config.preview_base_url}")

# Procesar certificado manualmente
>>> from certificates.services.pdf_processing import PDFProcessingService
>>> from certificates.models import Certificate
>>> service = PDFProcessingService()
>>> cert = Certificate.objects.get(uuid='...')
>>> result = service.process_qr_for_certificate(cert)
>>> print(result)
```

---

## ✅ Checklist de Uso

### Primera Vez
- [ ] Ejecutar `python manage.py load_qr_config`
- [ ] Verificar configuración en admin
- [ ] Crear evento de prueba
- [ ] Importar 1-2 PDFs de prueba
- [ ] Procesar QR
- [ ] Exportar
- [ ] Reimportar (simulando firma)
- [ ] Verificar preview público

### Uso Regular
- [ ] Importar PDFs del evento
- [ ] Revisar que se extrajeron nombres correctamente
- [ ] Procesar QR en lote
- [ ] Verificar que no hay errores
- [ ] Exportar para firma
- [ ] Guardar ZIP en lugar seguro
- [ ] Firmar certificados externamente
- [ ] Importar certificados firmados
- [ ] Verificar preview de algunos certificados
- [ ] Compartir URLs o QRs con participantes

---

## 🎉 ¡Listo para Usar!

El sistema está completamente funcional. Si tienes dudas o problemas, revisa:
1. Este documento
2. `PROCESAMIENTO_QR_IMPLEMENTADO.md` - Documentación técnica
3. `UI_PROCESAMIENTO_QR_COMPLETADA.md` - Detalles de implementación

**¡Disfruta procesando certificados con QR!** 🚀
