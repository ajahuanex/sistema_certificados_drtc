# Formato del Archivo Excel para Importación

Este documento describe en detalle el formato requerido para los archivos Excel de importación de participantes.

## Estructura del Archivo

### Columnas Requeridas

El archivo Excel **DEBE** contener exactamente estas columnas con estos nombres (sensible a mayúsculas y espacios):

| # | Nombre de Columna | Tipo de Dato | Obligatorio | Descripción |
|---|-------------------|--------------|-------------|-------------|
| 1 | DNI | Texto/Número | Sí | Documento Nacional de Identidad |
| 2 | Nombres y Apellidos | Texto | Sí | Nombre completo del participante |
| 3 | Fecha del Evento | Fecha | Sí | Fecha de realización del evento |
| 4 | Tipo de Asistente | Texto | Sí | Rol del participante en el evento |
| 5 | Nombre del Evento | Texto | Sí | Nombre completo del evento |

### Orden de las Columnas

Las columnas pueden estar en cualquier orden, pero los nombres deben ser exactos.

## Especificaciones por Columna

### 1. DNI

**Formato:** 8 dígitos numéricos

**Ejemplos válidos:**
- `12345678`
- `87654321`
- `00123456`

**Ejemplos inválidos:**
- `1234567` (solo 7 dígitos)
- `123456789` (9 dígitos)
- `1234567A` (contiene letra)
- `12.345.678` (contiene puntos)

**Notas:**
- Se aceptan ceros a la izquierda
- No se aceptan espacios ni caracteres especiales
- El formato de celda puede ser "Texto" o "Número"

### 2. Nombres y Apellidos

**Formato:** Texto libre

**Longitud:** Máximo 300 caracteres

**Ejemplos válidos:**
- `Juan Pérez García`
- `María del Carmen López Quispe`
- `Carlos Alberto Mamani Flores`

**Notas:**
- Se aceptan tildes y caracteres especiales
- Se recomienda usar el formato: Nombres + Apellido Paterno + Apellido Materno
- No puede estar vacío

### 3. Fecha del Evento

**Formatos aceptados:**
- `DD/MM/YYYY` (ejemplo: `15/10/2024`)
- `DD-MM-YYYY` (ejemplo: `15-10-2024`)
- `YYYY-MM-DD` (ejemplo: `2024-10-15`)
- Formato de fecha de Excel (número serial)

**Ejemplos válidos:**
- `15/10/2024`
- `01/01/2024`
- `31/12/2024`

**Ejemplos inválidos:**
- `15/13/2024` (mes inválido)
- `32/10/2024` (día inválido)
- `15-10-24` (año con 2 dígitos)
- `Octubre 15, 2024` (formato texto)

**Notas:**
- Se recomienda formatear la columna como "Fecha" en Excel
- Si usa formato de texto, usar DD/MM/YYYY
- El sistema detecta automáticamente el formato

### 4. Tipo de Asistente

**Valores permitidos (exactos, sensible a mayúsculas):**

| Valor | Descripción |
|-------|-------------|
| `ASISTENTE` | Participante regular del evento |
| `PONENTE` | Expositor o presentador |
| `ORGANIZADOR` | Organizador del evento |

**Ejemplos válidos:**
- `ASISTENTE`
- `PONENTE`
- `ORGANIZADOR`

**Ejemplos inválidos:**
- `asistente` (minúsculas)
- `Asistente` (capitalizado)
- `PARTICIPANTE` (valor no permitido)
- `EXPOSITOR` (valor no permitido)

**Notas:**
- Debe escribirse exactamente como se muestra (todo en mayúsculas)
- No se aceptan variaciones o sinónimos

### 5. Nombre del Evento

**Formato:** Texto libre

**Longitud:** Máximo 500 caracteres

**Ejemplos válidos:**
- `Capacitación en Seguridad Vial 2024`
- `Taller de Actualización en Normativa de Transporte`
- `Seminario Internacional de Infraestructura Vial`

**Notas:**
- Se aceptan tildes y caracteres especiales
- Debe ser descriptivo y único
- Si varios participantes tienen el mismo nombre de evento y fecha, se agruparán automáticamente

## Ejemplo Completo

### Archivo Excel de Ejemplo

```
| DNI      | Nombres y Apellidos      | Fecha del Evento | Tipo de Asistente | Nombre del Evento                    |
|----------|--------------------------|------------------|-------------------|--------------------------------------|
| 12345678 | Juan Pérez García        | 15/10/2024       | ASISTENTE         | Capacitación en Seguridad Vial 2024  |
| 87654321 | María López Quispe       | 15/10/2024       | PONENTE           | Capacitación en Seguridad Vial 2024  |
| 11223344 | Carlos Mamani Flores     | 15/10/2024       | ORGANIZADOR       | Capacitación en Seguridad Vial 2024  |
| 44332211 | Ana Torres Condori       | 15/10/2024       | ASISTENTE         | Capacitación en Seguridad Vial 2024  |
| 55667788 | Pedro Quispe Huanca      | 20/10/2024       | ASISTENTE         | Taller de Normativa de Transporte    |
| 99887766 | Rosa Mamani Apaza        | 20/10/2024       | PONENTE           | Taller de Normativa de Transporte    |
```

## Validaciones del Sistema

### Validaciones Automáticas

El sistema realiza las siguientes validaciones al importar:

1. **Estructura del archivo**
   - ✅ Verifica que existan todas las columnas requeridas
   - ✅ Verifica que los nombres de columnas sean exactos

2. **Validación por fila**
   - ✅ DNI: 8 dígitos numéricos
   - ✅ Nombres y Apellidos: No vacío, máximo 300 caracteres
   - ✅ Fecha del Evento: Fecha válida
   - ✅ Tipo de Asistente: Valor permitido
   - ✅ Nombre del Evento: No vacío, máximo 500 caracteres

3. **Validación de duplicados**
   - ✅ Si existe un participante con el mismo DNI en el mismo evento, se actualiza
   - ✅ Si es un evento diferente, se crea un nuevo registro

### Reporte de Errores

Si hay errores en el archivo, el sistema mostrará:

```
Importación completada con errores:

✅ Registros importados exitosamente: 4
❌ Registros con errores: 2

Detalle de errores:

Fila 5: DNI inválido. Debe tener 8 dígitos. Valor recibido: "1234567"
Fila 7: Tipo de Asistente inválido. Debe ser ASISTENTE, PONENTE u ORGANIZADOR. Valor recibido: "PARTICIPANTE"
```

## Mejores Prácticas

### Preparación del Archivo

1. **Usar plantilla**
   - Descarga la plantilla desde el panel de administración
   - No modifiques los nombres de las columnas

2. **Verificar datos antes de importar**
   - Revisa que todos los DNIs tengan 8 dígitos
   - Verifica que las fechas estén en formato correcto
   - Asegúrate de usar los valores exactos para Tipo de Asistente

3. **Formato de celdas**
   - DNI: Formato "Texto" (para preservar ceros a la izquierda)
   - Nombres y Apellidos: Formato "Texto"
   - Fecha del Evento: Formato "Fecha"
   - Tipo de Asistente: Formato "Texto"
   - Nombre del Evento: Formato "Texto"

4. **Limpieza de datos**
   - Elimina filas vacías
   - Elimina espacios extra al inicio y final
   - Verifica que no haya caracteres especiales no deseados

### Importación por Lotes

Para eventos grandes:

1. **Divide el archivo** si tiene más de 1000 participantes
2. **Importa en lotes** de 500-1000 registros
3. **Verifica** cada lote antes de continuar

### Actualización de Datos

Si necesitas actualizar datos de participantes ya importados:

1. **Usa el mismo archivo** con los datos corregidos
2. **Mantén el mismo DNI y Nombre del Evento**
3. **Importa nuevamente** - el sistema actualizará automáticamente

## Solución de Problemas Comunes

### Error: "Columnas faltantes"

**Causa:** Los nombres de las columnas no coinciden exactamente

**Solución:**
- Verifica que los nombres sean exactos (incluyendo mayúsculas y espacios)
- Copia los nombres de la plantilla oficial

### Error: "DNI inválido"

**Causa:** El DNI no tiene 8 dígitos o contiene caracteres no numéricos

**Solución:**
- Verifica que todos los DNIs tengan exactamente 8 dígitos
- Elimina puntos, guiones o espacios
- Agrega ceros a la izquierda si es necesario

### Error: "Tipo de Asistente inválido"

**Causa:** El valor no es uno de los permitidos o está en minúsculas

**Solución:**
- Usa exactamente: `ASISTENTE`, `PONENTE` o `ORGANIZADOR`
- Todo en mayúsculas
- Sin espacios extra

### Error: "Fecha inválida"

**Causa:** La fecha no está en un formato reconocido

**Solución:**
- Usa formato DD/MM/YYYY
- Formatea la columna como "Fecha" en Excel
- Verifica que la fecha sea válida (no 32/13/2024)

## Plantilla de Excel

Puedes descargar una plantilla de ejemplo desde:

- Panel de administración → Import Excel → Download Template
- O crear un archivo con la estructura mostrada arriba

## Preguntas Frecuentes

### ¿Puedo agregar columnas adicionales?

Sí, puedes agregar columnas adicionales, pero serán ignoradas. Las 5 columnas requeridas deben estar presentes.

### ¿El orden de las columnas importa?

No, las columnas pueden estar en cualquier orden, siempre que los nombres sean correctos.

### ¿Puedo usar archivos .xls (Excel 97-2003)?

Sí, se aceptan tanto .xlsx como .xls

### ¿Cuál es el tamaño máximo del archivo?

El tamaño máximo es 10 MB. Para archivos más grandes, divide en múltiples archivos.

### ¿Qué pasa si importo el mismo archivo dos veces?

Los participantes existentes se actualizarán con los nuevos datos. No se crearán duplicados.

### ¿Puedo importar participantes de múltiples eventos en un solo archivo?

Sí, simplemente usa diferentes valores en la columna "Nombre del Evento" y/o "Fecha del Evento".

## Soporte

Si tienes problemas con la importación:

1. Verifica que tu archivo cumpla con todos los requisitos
2. Revisa el reporte de errores detallado
3. Consulta esta documentación
4. Contacta al administrador del sistema

---

**Última actualización:** 28 de octubre de 2024
