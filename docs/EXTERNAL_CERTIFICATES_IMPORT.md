# 📥 Guía de Importación de Certificados Externos

## Descripción

Esta funcionalidad permite importar certificados que fueron generados en otros sistemas. Solo necesitas proporcionar la URL donde está alojado cada certificado y el sistema generará automáticamente códigos QR para verificación.

## ¿Cuándo usar esta funcionalidad?

- **Migración de sistemas**: Cuando estás migrando de un sistema antiguo y quieres mantener el historial
- **Certificados de terceros**: Cuando necesitas registrar certificados emitidos por otras instituciones
- **Integración con otros sistemas**: Para mantener un registro centralizado de todos los certificados
- **Consulta unificada**: Los participantes pueden consultar todos sus certificados en un solo lugar

## Características

✅ **No almacena PDFs**: Los certificados externos no se almacenan en este sistema, solo se registra su URL  
✅ **Genera QR automáticamente**: Se crea un código QR que apunta a la URL externa del certificado  
✅ **Consulta integrada**: Los participantes pueden consultar certificados internos y externos por DNI  
✅ **Actualización automática**: Si un participante ya tiene un certificado, se actualiza con la nueva URL  
✅ **Redirección transparente**: Al hacer clic en "Descargar", se redirige a la URL externa  

## Formato del Archivo Excel

### Columnas Requeridas

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| **DNI** | Texto/Número | Documento Nacional de Identidad (8 dígitos) | 12345678 |
| **Nombres y Apellidos** | Texto | Nombre completo del participante | Juan Pérez García |
| **Fecha del Evento** | Fecha | Fecha en que se realizó el evento | 15/10/2024 |
| **Tipo de Asistente** | Texto | Rol del participante | ASISTENTE |
| **Nombre del Evento** | Texto | Nombre completo del evento | Capacitación en Seguridad Vial |
| **URL del Certificado** | URL | URL completa donde está alojado el certificado | https://sistema-antiguo.com/certs/12345.pdf |

### Columnas Opcionales

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| **Sistema Externo** | Nombre del sistema del que proviene | Sistema Antiguo v1.0 |

## Ejemplo de Archivo Excel

```
| DNI      | Nombres y Apellidos    | Fecha del Evento | Tipo de Asistente | Nombre del Evento                | URL del Certificado                                    | Sistema Externo    |
|----------|------------------------|------------------|-------------------|----------------------------------|--------------------------------------------------------|--------------------|
| 12345678 | Juan Pérez García      | 15/10/2024       | ASISTENTE         | Capacitación en Seguridad Vial   | https://sistema-antiguo.com/certs/12345678_2024.pdf   | Sistema Antiguo    |
| 87654321 | María López Quispe     | 15/10/2024       | PONENTE           | Capacitación en Seguridad Vial   | https://sistema-antiguo.com/certs/87654321_2024.pdf   | Sistema Antiguo    |
| 11223344 | Carlos Mamani Flores   | 15/10/2024       | ORGANIZADOR       | Capacitación en Seguridad Vial   | https://sistema-antiguo.com/certs/11223344_2024.pdf   | Sistema Antiguo    |
```

## Validaciones

El sistema validará automáticamente:

1. ✅ **DNI**: Debe tener exactamente 8 dígitos numéricos
2. ✅ **Nombres y Apellidos**: No puede estar vacío
3. ✅ **Fecha del Evento**: Debe ser una fecha válida
4. ✅ **Tipo de Asistente**: Debe ser ASISTENTE, PONENTE u ORGANIZADOR
5. ✅ **Nombre del Evento**: No puede estar vacío
6. ✅ **URL del Certificado**: Debe comenzar con http:// o https://

## Formatos de Fecha Aceptados

- `DD/MM/YYYY` (ejemplo: 15/10/2024)
- `DD-MM-YYYY` (ejemplo: 15-10-2024)
- `YYYY-MM-DD` (ejemplo: 2024-10-15)

## Proceso de Importación

### Paso 1: Preparar el Archivo Excel

1. Crea un archivo Excel (.xlsx o .xls)
2. Agrega las columnas requeridas en la primera fila
3. Completa los datos de cada participante
4. Asegúrate de que las URLs sean accesibles públicamente

### Paso 2: Acceder a la Importación

1. Inicia sesión en el panel de administración
2. Ve a: http://tu-dominio.com/admin/import-external/
3. O busca "Importar Certificados Externos" en el menú

### Paso 3: Subir el Archivo

1. Haz clic en "Choose File" y selecciona tu archivo Excel
2. Haz clic en "Importar Certificados Externos"
3. Espera a que el sistema procese el archivo

### Paso 4: Revisar Resultados

El sistema mostrará:
- ✅ Número de certificados importados exitosamente
- ℹ️ Número de certificados existentes actualizados
- ❌ Número de errores encontrados
- 📋 Detalle de cada error (si los hay)

## Manejo de Duplicados

- Si un participante con el mismo DNI ya tiene un certificado para el mismo evento, se **actualizará** con la nueva URL externa
- Si es un evento diferente, se creará un nuevo registro de certificado
- Los certificados internos pueden ser reemplazados por externos y viceversa

## Códigos QR

Para cada certificado externo importado, el sistema:

1. Genera automáticamente un código QR
2. El QR apunta directamente a la URL externa del certificado
3. El QR se almacena en el sistema para consultas futuras
4. Los participantes pueden escanear el QR para acceder al certificado

## Consulta Pública

Los certificados externos se integran completamente con la consulta pública:

1. Los participantes consultan por DNI como siempre
2. Se muestran todos los certificados (internos y externos)
3. Los certificados externos tienen un badge "Externo"
4. Al hacer clic en "Descargar", se redirige a la URL externa

## Ejemplo de Uso: Migración de Sistema

### Escenario

Tienes 500 certificados en un sistema antiguo alojados en:
`https://sistema-antiguo.com/certificados/`

### Solución

1. Exporta los datos del sistema antiguo a Excel
2. Agrega la columna "URL del Certificado" con las URLs completas
3. Importa el archivo en el nuevo sistema
4. Los participantes pueden consultar todos sus certificados en un solo lugar

### Ventajas

- ✅ No necesitas migrar los archivos PDF
- ✅ Mantienes el historial completo
- ✅ Los certificados antiguos siguen accesibles
- ✅ Consulta unificada para los participantes

## Errores Comunes y Soluciones

### Error: "DNI inválido"

**Causa**: El DNI no tiene 8 dígitos o contiene caracteres no numéricos

**Solución**: Asegúrate de que el DNI tenga exactamente 8 dígitos numéricos

### Error: "URL del Certificado inválida"

**Causa**: La URL no comienza con http:// o https://

**Solución**: Verifica que todas las URLs sean completas y válidas

### Error: "Tipo de Asistente inválido"

**Causa**: El valor no es ASISTENTE, PONENTE u ORGANIZADOR

**Solución**: Usa solo los valores permitidos (en mayúsculas)

### Error: "Formato de fecha inválido"

**Causa**: La fecha no está en un formato reconocido

**Solución**: Usa uno de los formatos aceptados (DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD)

## Reporte de Errores

Después de la importación, el sistema mostrará:

- ✅ Registros importados exitosamente
- ℹ️ Registros actualizados
- ❌ Registros con errores
- 📋 Detalle de cada error por fila

Si hay errores:
1. Revisa el reporte de errores mostrado
2. Corrige los datos en el archivo Excel
3. Vuelve a importar el archivo (solo las filas con error)

## Mejores Prácticas

### 1. Verificar URLs

Antes de importar, verifica que:
- Las URLs sean accesibles públicamente
- Los certificados estén disponibles en las URLs
- Las URLs no expiren o cambien

### 2. Mantener Respaldo

- Guarda una copia del archivo Excel original
- Documenta el sistema de origen
- Mantén un registro de las URLs

### 3. Importación Gradual

Para grandes volúmenes:
- Importa en lotes de 100-200 registros
- Verifica cada lote antes de continuar
- Corrige errores inmediatamente

### 4. Nombrar Archivos

Usa nombres descriptivos:
- `certificados_externos_2024_lote1.xlsx`
- `migracion_sistema_antiguo_parte1.xlsx`

## Limitaciones

- ⚠️ Los certificados externos no pueden ser firmados digitalmente por este sistema
- ⚠️ No se puede regenerar el PDF de certificados externos
- ⚠️ La disponibilidad depende del sistema externo
- ⚠️ No se pueden editar los PDFs externos desde este sistema

## Preguntas Frecuentes

### ¿Puedo importar certificados de múltiples sistemas?

Sí, usa la columna "Sistema Externo" para identificar el origen de cada certificado.

### ¿Qué pasa si la URL externa deja de funcionar?

El certificado seguirá registrado en el sistema, pero el enlace no funcionará. Deberás actualizar la URL.

### ¿Puedo convertir un certificado externo en interno?

Sí, puedes generar un nuevo certificado interno que reemplazará al externo.

### ¿Los certificados externos aparecen en el dashboard?

Sí, se incluyen en todas las estadísticas y reportes del sistema.

### ¿Puedo importar certificados sin evento?

No, todos los certificados deben estar asociados a un evento. El sistema creará el evento automáticamente si no existe.

## Soporte

Para problemas o preguntas:
- Revisa los logs del sistema
- Consulta la documentación del proyecto
- Contacta al equipo de desarrollo

## Recursos Adicionales

- [Guía de Administrador](ADMIN_GUIDE.md)
- [Formato de Excel](EXCEL_FORMAT.md)
- [Comandos de Management](MANAGEMENT_COMMANDS.md)
