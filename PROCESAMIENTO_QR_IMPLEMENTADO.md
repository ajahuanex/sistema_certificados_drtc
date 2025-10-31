# 🎯 Procesamiento de Certificados con QR - Implementación

## ✅ Tareas Completadas (3/3 del MVP)

### 1️⃣ Modelo Certificate Extendido ✅

**Campos agregados:**
- `processing_status` - Estados: IMPORTED, QR_GENERATED, QR_INSERTED, EXPORTED_FOR_SIGNING, SIGNED_FINAL, ERROR
- `original_pdf` - PDF original sin QR
- `qr_pdf` - PDF con QR insertado (listo para firma)
- `final_pdf` - PDF firmado final (para preview público)
- `qr_image` - Imagen del código QR generado
- `qr_position_x`, `qr_position_y`, `qr_size` - Configuración de posicionamiento
- `processing_errors` - Errores durante el procesamiento
- `processed_at`, `exported_at`, `final_imported_at` - Timestamps

**Métodos agregados:**
- `get_preview_url()` - URL de preview del certificado
- `can_process_qr()` - Verifica si puede procesar QR
- `can_export_for_signing()` - Verifica si puede exportarse
- `can_import_final()` - Verifica si puede recibir versión final
- `is_ready_for_preview()` - Verifica si está listo para preview público
- `get_current_pdf()` - Retorna el PDF actual según el estado
- `get_processing_progress()` - Progreso como porcentaje (0-100)
- `mark_processing_error()` - Marca errores de procesamiento

**Migración:** `0004_certificate_exported_at_and_more.py` ✅

---

### 2️⃣ Modelo QRProcessingConfig Creado ✅

**Configuración de Posicionamiento:**
- `default_qr_x` = 450 (píxeles desde la izquierda)
- `default_qr_y` = 50 (píxeles desde arriba)
- `default_qr_size` = 100 (tamaño en píxeles)

**Configuración de Calidad:**
- `qr_error_correction` - Nivel: L (7%), M (15%), Q (25%), H (30%)
- `qr_border` = 2 (tamaño del borde)
- `qr_box_size` = 10 (tamaño de cada módulo)

**Configuración de URL:**
- `preview_base_url` = 'http://localhost:8000'

**Opciones de Procesamiento:**
- `enable_qr_validation` = True (validar legibilidad)
- `enable_pdf_backup` = True (crear respaldos)
- `max_pdf_size_mb` = 10 (tamaño máximo)

**Métodos útiles:**
- `get_qr_preview_url(certificate_uuid)` - Construye URL completa
- `validate_pdf_size(file_size_bytes)` - Valida tamaño
- `get_qr_settings()` - Retorna configuración del QR
- `get_position_settings()` - Retorna configuración de posición
- `get_active_config()` - Obtiene configuración activa (o crea una por defecto)

**Extras:**
- Comando de gestión: `python manage.py load_qr_config`
- Admin registrado con interfaz completa
- Solo una configuración puede estar activa a la vez

**Migración:** `0005_qrprocessingconfig.py` ✅

---

### 3️⃣ Servicio PDFProcessingService Implementado ✅

**Importación de PDFs:**
```python
service.import_pdf_batch(
    pdf_files=[...],
    event=event,
    auto_extract_names=True
)
```
- Importa múltiples PDFs de forma masiva
- Extrae nombres automáticamente (del archivo o contenido PDF)
- Valida tamaño y formato
- Crea participantes automáticamente si no existen

**Procesamiento de QR:**
```python
service.process_qr_for_certificate(certificate, config)
```
- Genera código QR con URL de preview
- Inserta QR en PDF usando PyPDF2 + reportlab
- Valida legibilidad del QR
- Actualiza estado a QR_INSERTED

**Exportación para Firma:**
```python
zip_bytes, filename = service.create_export_zip(certificates)
```
- Crea ZIP con certificados para firma externa
- Incluye CSV con metadatos (UUID, DNI, nombre, evento)
- Nombres de archivo con UUID para facilitar reimportación
- Actualiza estado a EXPORTED_FOR_SIGNING

**Importación Final:**
```python
service.import_final_certificates(pdf_files)
```
- Importa certificados firmados
- Extrae UUID del nombre de archivo
- Actualiza estado a SIGNED_FINAL
- Habilita para preview público

**Dependencia agregada:** `PyPDF2>=3.0` ✅

---

## 🔄 Flujo Completo Implementado

```
1. IMPORTAR PDFs
   ↓
   [PDF Original] → Estado: IMPORTED
   
2. PROCESAR QR
   ↓
   [Generar QR] → [Insertar en PDF] → Estado: QR_INSERTED
   
3. EXPORTAR
   ↓
   [Crear ZIP] → Estado: EXPORTED_FOR_SIGNING
   
4. FIRMA EXTERNA (Manual)
   ↓
   [Firmar PDFs fuera del sistema]
   
5. IMPORTAR FINAL
   ↓
   [PDF Firmado] → Estado: SIGNED_FINAL
   
6. PREVIEW PÚBLICO
   ↓
   [URL: /certificado/{uuid}/preview/]
```

---

## 📊 Estado Actual

✅ **Backend completo** - Modelos y servicios listos  
⏳ **Vistas pendientes** - Interfaces de administración  
⏳ **Templates pendientes** - UI para importar/exportar  
⏳ **URLs pendientes** - Rutas para las vistas  
⏳ **Tests pendientes** - Pruebas unitarias e integración  

---

## 🚀 Próximas Tareas Sugeridas (MVP)

### Opción A: Completar Funcionalidad Básica (Recomendado)
1. **Crear vistas de administración** - Para importar PDFs y procesar QR
2. **Crear templates** - Interfaces para el flujo completo
3. **Configurar URLs** - Rutas para las vistas
4. **Vista de preview público** - Para que usuarios vean certificados

### Opción B: Agregar Tests
1. **Tests unitarios** - Para servicios y modelos
2. **Tests de integración** - Para flujo completo

### Opción C: Documentación
1. **Guía de usuario** - Cómo usar el sistema
2. **Documentación técnica** - APIs y servicios

---

## 💡 Cómo Usar (Cuando esté completo)

### 1. Configurar QR
```bash
python manage.py load_qr_config
```

### 2. Importar PDFs (Desde Admin)
- Ir a Admin → Certificados → Importar PDFs
- Seleccionar evento
- Subir múltiples PDFs
- Sistema extrae nombres automáticamente

### 3. Procesar QR (Desde Admin)
- Seleccionar certificados en estado IMPORTED
- Acción: "Procesar QR"
- Sistema genera QR e inserta en PDF

### 4. Exportar para Firma (Desde Admin)
- Seleccionar certificados en estado QR_INSERTED
- Acción: "Exportar para Firma"
- Descargar ZIP con PDFs y metadata.csv

### 5. Firmar Externamente
- Firmar PDFs con herramienta externa
- Mantener nombres de archivo (incluyen UUID)

### 6. Importar Finales (Desde Admin)
- Ir a Admin → Certificados → Importar Finales
- Subir PDFs firmados
- Sistema identifica por UUID y actualiza

### 7. Preview Público
- URL: `https://tu-dominio.com/certificado/{uuid}/preview/`
- Escanear QR del certificado
- Ver certificado verificado

---

## 🔧 Comandos Útiles

```bash
# Crear configuración inicial
python manage.py load_qr_config

# Ver configuración activa
python manage.py shell
>>> from certificates.models import QRProcessingConfig
>>> config = QRProcessingConfig.get_active_config()
>>> print(config)

# Procesar certificado manualmente
>>> from certificates.services.pdf_processing import PDFProcessingService
>>> service = PDFProcessingService()
>>> result = service.process_qr_for_certificate(certificate)
```

---

## 📝 Notas Técnicas

### Extracción de Nombres
El sistema intenta extraer nombres de:
1. Nombre del archivo (limpiando caracteres especiales)
2. Contenido del PDF (buscando patrones como "Certificado de:", "Otorgado a:", etc.)
3. Si falla, usa el nombre del archivo como fallback

### Validaciones
- Tamaño máximo de PDF: 10 MB (configurable)
- Validación de integridad del PDF
- Validación de legibilidad del QR generado
- Validación de estados antes de cada operación

### Seguridad
- Solo staff puede acceder a funciones de procesamiento
- Preview público solo para certificados en estado SIGNED_FINAL
- Respaldos automáticos de PDFs originales
- Logs de auditoría para todas las operaciones

---

## 🎨 Personalización

### Cambiar Posición del QR
```python
# Desde Admin o código
config = QRProcessingConfig.get_active_config()
config.default_qr_x = 500  # Más a la derecha
config.default_qr_y = 100  # Más abajo
config.default_qr_size = 120  # Más grande
config.save()
```

### Cambiar URL Base
```python
config = QRProcessingConfig.get_active_config()
config.preview_base_url = 'https://certificados.drtcpuno.gob.pe'
config.save()
```

---

## ✨ Características Destacadas

- ✅ Procesamiento masivo de PDFs
- ✅ Extracción inteligente de nombres
- ✅ Inserción precisa de QR en PDFs
- ✅ Exportación con metadatos para trazabilidad
- ✅ Reimportación automática por UUID
- ✅ Configuración flexible y centralizada
- ✅ Validaciones robustas en cada paso
- ✅ Manejo de errores detallado
- ✅ Estados claros del flujo de procesamiento
- ✅ Preview público con verificación

---

**Fecha de implementación:** $(date)  
**Versión:** 1.0.0  
**Estado:** Backend completo, pendiente UI
