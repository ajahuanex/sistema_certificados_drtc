# ✅ IMPORTACIÓN CSV CON VALIDACIÓN IMPLEMENTADA

## Fecha: 18 de Noviembre de 2025

## 🎯 Funcionalidades Implementadas

### 1. **Importación desde CSV** ✅

**Características**:
- ✅ Soporte completo para archivos CSV
- ✅ Validación previa antes de importar
- ✅ Normalización automática de DNI con ceros
- ✅ Vista previa de datos a importar
- ✅ Mensajes detallados de errores y advertencias
- ✅ Opción de "Solo validar" sin importar

### 2. **Normalización de DNI** ✅

**En todos los importadores**:
- ✅ Excel Processor - Normaliza DNI
- ✅ CSV Processor - Normaliza DNI
- ✅ External Certificate Importer - Normaliza DNI

**Comportamiento**:
- DNI `1234567` → `01234567`
- DNI `00123456` → `00123456`
- DNI `123` → `00000123`

### 3. **Validación Previa** ✅

**Validaciones Implementadas**:
- ✅ Formato de DNI (1-8 dígitos numéricos)
- ✅ Nombre completo no vacío
- ✅ Tipo de asistente válido (ASISTENTE, PONENTE, ORGANIZADOR)
- ✅ Formato de fecha correcto
- ✅ Nombre del evento no vacío
- ✅ Detección de filas vacías

---

## 📋 Cómo Usar

### Importar desde CSV

1. **Ir al Admin de Participantes**:
   - URL: https://certificados.transportespuno.gob.pe/admin/certificates/participant/

2. **Hacer clic en "Importar desde CSV"** (botón en la parte superior)

3. **Seleccionar archivo CSV**:
   - Formato: CSV separado por comas
   - Codificación: UTF-8
   - Tamaño máximo: 10MB

4. **Opción 1: Solo Validar**:
   - Marcar checkbox "Solo validar (no importar)"
   - Hacer clic en "Procesar Archivo"
   - Ver resultados de validación
   - Corregir errores si es necesario

5. **Opción 2: Importar Directamente**:
   - No marcar checkbox
   - Hacer clic en "Procesar Archivo"
   - Los datos se importarán inmediatamente

---

## 📄 Formato del Archivo CSV

### Columnas Requeridas

```csv
DNI,Nombres y Apellidos,Fecha del Evento,Tipo de Asistente,Nombre del Evento
1234567,Juan Pérez García,15/11/2025,ASISTENTE,Capacitación 2025
00123456,María López,15/11/2025,PONENTE,Capacitación 2025
987654,Carlos Rodríguez,15/11/2025,ORGANIZADOR,Capacitación 2025
```

### Especificaciones

| Columna | Tipo | Formato | Ejemplo |
|---------|------|---------|---------|
| DNI | Numérico | 1-8 dígitos | 1234567, 00123456 |
| Nombres y Apellidos | Texto | Cualquier texto | Juan Pérez García |
| Fecha del Evento | Fecha | DD/MM/YYYY | 15/11/2025 |
| Tipo de Asistente | Texto | ASISTENTE, PONENTE, ORGANIZADOR | ASISTENTE |
| Nombre del Evento | Texto | Cualquier texto | Capacitación 2025 |

### Formatos de Fecha Soportados

- `DD/MM/YYYY` → 15/11/2025
- `DD-MM-YYYY` → 15-11-2025
- `YYYY-MM-DD` → 2025-11-15
- `DD/MM/YY` → 15/11/25
- `YYYY/MM/DD` → 2025/11/15

---

## 🔍 Validación Previa

### Qué se Valida

**DNI**:
- ✅ Contiene solo dígitos numéricos
- ✅ No tiene más de 8 dígitos
- ⚠️ Se normaliza con ceros a la izquierda

**Nombre**:
- ✅ No está vacío
- ✅ Contiene texto válido

**Tipo de Asistente**:
- ✅ Es uno de: ASISTENTE, PONENTE, ORGANIZADOR
- ✅ No distingue mayúsculas/minúsculas

**Fecha**:
- ✅ Formato válido
- ✅ Fecha parseable

**Evento**:
- ✅ Nombre no vacío

### Mensajes de Validación

**Errores** (en rojo):
- `Fila 5: DNI '12345678901' no puede tener más de 8 dígitos`
- `Fila 7: Tipo de Asistente 'INVITADO' no es válido`
- `Fila 10: Formato de fecha inválido: '32/13/2025'`

**Advertencias** (en amarillo):
- `Fila 3: DNI '1234567' se normalizará a '01234567'`
- `Fila 8: DNI '123' se normalizará a '00000123'`

**Éxitos** (en verde):
- `Fila 2: ✓ Válido`

---

## 📊 Vista Previa de Resultados

Después de validar, se muestra:

1. **Resumen General**:
   - Total de filas válidas
   - Total de errores
   - Total de advertencias

2. **Lista de Mensajes**:
   - Todos los errores y advertencias
   - Coloreados por tipo

3. **Tabla de Vista Previa**:
   - Primeras 10 filas
   - Datos normalizados
   - Estado de cada fila (✓ Válido / ✗ Error)

---

## 🔧 Archivos Creados/Modificados

### Nuevos Archivos

1. **`certificates/services/csv_processor.py`**
   - Procesador de archivos CSV
   - Validación completa
   - Normalización de DNI

2. **`templates/admin/certificates/csv_import.html`**
   - Formulario de importación
   - Instrucciones detalladas
   - Ejemplos de formato

3. **`templates/admin/certificates/csv_validation_result.html`**
   - Resultados de validación
   - Vista previa de datos
   - Mensajes coloreados

### Archivos Modificados

1. **`certificates/forms.py`**
   - Agregado `CSVImportForm`
   - Validación de archivo CSV
   - Opción de "Solo validar"

2. **`certificates/admin.py`**
   - Agregado método `import_csv_view` en ParticipantAdmin
   - URL personalizada para importación
   - Integración con el admin

3. **`certificates/services/excel_processor.py`**
   - Agregado método `_normalize_dni`
   - Validación mejorada de DNI
   - Normalización automática

4. **`certificates/services/external_certificate_importer.py`**
   - Agregado método `_normalize_dni`
   - Validación mejorada de DNI
   - Normalización automática

---

## 🎯 Casos de Uso

### Caso 1: Validar Antes de Importar

**Problema**: Tienes un archivo CSV grande y quieres asegurarte de que no tiene errores.

**Solución**:
1. Ir a Admin > Participantes > Importar desde CSV
2. Seleccionar archivo
3. Marcar "Solo validar"
4. Hacer clic en "Procesar Archivo"
5. Revisar resultados
6. Corregir errores en el archivo
7. Volver a validar
8. Cuando esté todo correcto, importar sin marcar "Solo validar"

### Caso 2: Importar con DNI con Ceros

**Problema**: Tu archivo tiene DNI como `1234567` pero necesitas que se guarden como `01234567`.

**Solución**:
- El sistema normaliza automáticamente
- No necesitas modificar el archivo
- Se mostrará una advertencia informativa
- Los DNI se guardarán correctamente con ceros

### Caso 3: Detectar Errores Rápidamente

**Problema**: Tienes 1000 filas y quieres saber si hay errores.

**Solución**:
1. Usar "Solo validar"
2. Ver lista completa de errores
3. Corregir en el archivo original
4. Volver a validar
5. Importar cuando esté limpio

---

## ⚠️ Consideraciones Importantes

### Codificación del Archivo

- **Recomendado**: UTF-8 con BOM
- **Soportado**: UTF-8, UTF-8-SIG
- **Problema común**: Si ves caracteres raros (ñ, á, é), el archivo no está en UTF-8

**Solución en Excel**:
1. Abrir el archivo
2. Guardar como → CSV UTF-8 (delimitado por comas)

### Separador de Columnas

- **Debe ser**: Coma (,)
- **No usar**: Punto y coma (;) o tabulador

### Filas Vacías

- Se ignoran automáticamente
- No generan errores

### Duplicados

- Si un participante ya existe (mismo DNI + mismo evento):
  - Se actualizan sus datos
  - No se crea duplicado

---

## 📞 Comandos Útiles

### Crear Archivo CSV de Ejemplo

```python
import csv

data = [
    ['DNI', 'Nombres y Apellidos', 'Fecha del Evento', 'Tipo de Asistente', 'Nombre del Evento'],
    ['1234567', 'Juan Pérez García', '15/11/2025', 'ASISTENTE', 'Capacitación 2025'],
    ['00123456', 'María López', '15/11/2025', 'PONENTE', 'Capacitación 2025'],
    ['987654', 'Carlos Rodríguez', '15/11/2025', 'ORGANIZADOR', 'Capacitación 2025'],
]

with open('participantes.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerows(data)
```

### Validar CSV desde Python

```python
from certificates.services.csv_processor import CSVProcessorService

service = CSVProcessorService()

with open('participantes.csv', 'rb') as f:
    is_valid, messages, validated_rows = service.validate_file(f)
    
    print(f"Válido: {is_valid}")
    print(f"Total filas: {len(validated_rows)}")
    
    for msg in messages:
        print(msg)
```

---

## 🚀 Próximas Mejoras Sugeridas

- [ ] Importación de certificados externos desde CSV
- [ ] Exportación de participantes a CSV
- [ ] Plantilla CSV descargable
- [ ] Importación con mapeo de columnas personalizado
- [ ] Importación desde Google Sheets
- [ ] Validación de DNI contra RENIEC (API)
- [ ] Detección automática de codificación
- [ ] Soporte para más formatos de fecha

---

## ✅ Checklist de Implementación

- [x] Crear CSVProcessorService
- [x] Agregar normalización de DNI
- [x] Crear formulario CSVImportForm
- [x] Agregar vista de importación en admin
- [x] Crear plantilla de importación
- [x] Crear plantilla de resultados
- [x] Actualizar Excel processor
- [x] Actualizar External importer
- [x] Documentación completa
- [x] Subir a GitHub
- [ ] Actualizar servidor de producción
- [ ] Probar en producción

---

**Sistema de Certificados DRTC - Importación CSV Completa** ✅
