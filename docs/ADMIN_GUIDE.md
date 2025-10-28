# Guía de Usuario para Administradores

Esta guía proporciona instrucciones detalladas para administradores del Sistema de Certificados DRTC Puno.

## Tabla de Contenidos

- [Acceso al Sistema](#acceso-al-sistema)
- [Panel de Administración](#panel-de-administración)
- [Gestión de Eventos](#gestión-de-eventos)
- [Importación de Participantes](#importación-de-participantes)
- [Gestión de Participantes](#gestión-de-participantes)
- [Generación de Certificados](#generación-de-certificados)
- [Firma Digital de Certificados](#firma-digital-de-certificados)
- [Gestión de Plantillas](#gestión-de-plantillas)
- [Auditoría y Logs](#auditoría-y-logs)
- [Flujo de Trabajo Completo](#flujo-de-trabajo-completo)
- [Mejores Prácticas](#mejores-prácticas)
- [Solución de Problemas](#solución-de-problemas)

## Acceso al Sistema

### Inicio de Sesión

1. Abre tu navegador web
2. Navega a: `https://certificados.drtcpuno.gob.pe/admin/`
3. Ingresa tu nombre de usuario
4. Ingresa tu contraseña
5. Haz clic en "Log in"

### Recuperación de Contraseña

Si olvidaste tu contraseña:

1. Contacta al administrador del sistema
2. El administrador puede restablecer tu contraseña usando:
   ```bash
   python manage.py changepassword tu_usuario
   ```

### Cambio de Contraseña

Para cambiar tu contraseña:

1. Inicia sesión en el panel de administración
2. Haz clic en tu nombre de usuario (esquina superior derecha)
3. Selecciona "Change password"
4. Ingresa tu contraseña actual
5. Ingresa tu nueva contraseña dos veces
6. Haz clic en "Change my password"

## Panel de Administración

### Navegación Principal

El panel de administración está organizado en secciones:

```
CERTIFICATES
├── Events                    # Gestión de eventos
├── Participants             # Gestión de participantes
├── Certificates             # Gestión de certificados
├── Certificate Templates    # Gestión de plantillas
├── Audit Logs              # Registro de auditoría
└── Import Excel            # Importación de participantes
```

### Interfaz de Usuario

- **Barra superior**: Navegación, usuario actual, cerrar sesión
- **Menú lateral**: Acceso a todas las secciones
- **Área principal**: Contenido de la sección actual
- **Breadcrumbs**: Navegación jerárquica

## Gestión de Eventos

### Crear un Nuevo Evento

1. En el panel de administración, haz clic en **"Events"**
2. Haz clic en el botón **"Add Event"** (esquina superior derecha)
3. Completa el formulario:

   **Campos obligatorios:**
   - **Name**: Nombre descriptivo del evento
     - Ejemplo: "Capacitación en Seguridad Vial 2024"
   - **Event date**: Fecha de realización del evento
     - Usa el selector de fecha o ingresa manualmente (DD/MM/YYYY)
   - **Template**: Selecciona la plantilla de certificado
     - Por defecto: "Plantilla DRTC Puno"

   **Campos opcionales:**
   - **Description**: Descripción detallada del evento
     - Ejemplo: "Capacitación dirigida a conductores profesionales sobre normativa de seguridad vial vigente"

4. Haz clic en **"Save"** para crear el evento
5. O haz clic en **"Save and add another"** para crear otro evento inmediatamente

### Listar Eventos

1. Haz clic en **"Events"** en el menú principal
2. Verás una tabla con todos los eventos:
   - Nombre del evento
   - Fecha del evento
   - Número de participantes
   - Plantilla utilizada
   - Fecha de creación

### Buscar Eventos

En la lista de eventos:

1. Usa la barra de búsqueda (esquina superior derecha)
2. Puedes buscar por:
   - Nombre del evento
   - Descripción

### Filtrar Eventos

En la lista de eventos:

1. Usa los filtros del panel derecho:
   - **Por fecha del evento**: Hoy, últimos 7 días, este mes, este año
   - **Por plantilla**: Filtra por plantilla de certificado
   - **Por fecha de creación**: Filtra por cuándo se creó el registro

### Editar un Evento

1. En la lista de eventos, haz clic en el evento que deseas editar
2. Modifica los campos necesarios
3. Haz clic en **"Save"** para guardar los cambios

**Nota:** Si modificas la fecha o nombre del evento después de generar certificados, considera regenerar los certificados.

### Eliminar un Evento

⚠️ **Advertencia:** Eliminar un evento también eliminará todos sus participantes y certificados asociados.

1. En la lista de eventos, marca el checkbox del evento a eliminar
2. En el menú desplegable de acciones, selecciona **"Delete selected events"**
3. Haz clic en **"Go"**
4. Confirma la eliminación

### Generar Certificados para un Evento

Desde la lista de eventos:

1. Marca el checkbox del evento
2. En el menú desplegable de acciones, selecciona **"Generar Certificados"**
3. Haz clic en **"Go"**
4. El sistema generará certificados para todos los participantes del evento
5. Verás un mensaje de confirmación:
   ```
   ✅ Se generaron 45 certificados exitosamente para el evento "Capacitación en Seguridad Vial 2024"
   ```

## Importación de Participantes

### Preparar el Archivo Excel

Antes de importar, asegúrate de que tu archivo Excel cumpla con el formato requerido.

**Columnas requeridas:**
- DNI
- Nombres y Apellidos
- Fecha del Evento
- Tipo de Asistente (ASISTENTE, PONENTE, ORGANIZADOR)
- Nombre del Evento

Ver [Formato del Archivo Excel](EXCEL_FORMAT.md) para detalles completos.

### Importar Participantes

1. En el panel de administración, haz clic en **"Import Excel"**
2. Verás la página de importación con:
   - Instrucciones sobre el formato requerido
   - Botón para seleccionar archivo
   - Enlace para descargar plantilla de ejemplo

3. Haz clic en **"Choose File"** y selecciona tu archivo Excel
4. Haz clic en **"Import"**
5. El sistema procesará el archivo (puede tomar unos segundos)

### Interpretar Resultados de Importación

Después de la importación, verás un reporte:

**Importación exitosa:**
```
✅ Importación completada exitosamente

Registros importados: 45
Registros actualizados: 3
Total procesado: 48
```

**Importación con errores:**
```
⚠️ Importación completada con errores

✅ Registros importados exitosamente: 42
❌ Registros con errores: 6

Detalle de errores:

Fila 5: DNI inválido. Debe tener 8 dígitos. Valor recibido: "1234567"
Fila 12: Tipo de Asistente inválido. Debe ser ASISTENTE, PONENTE u ORGANIZADOR. Valor recibido: "PARTICIPANTE"
Fila 18: Fecha del Evento inválida. Formato esperado: DD/MM/YYYY. Valor recibido: "15-Oct-2024"
Fila 23: Nombres y Apellidos no puede estar vacío
Fila 31: DNI inválido. Debe tener 8 dígitos. Valor recibido: "123456789"
Fila 45: Nombre del Evento no puede estar vacío
```

### Corregir Errores de Importación

Si hay errores:

1. Anota los números de fila con errores
2. Abre el archivo Excel original
3. Corrige los datos en las filas indicadas
4. Guarda el archivo
5. Vuelve a importar

**Tip:** Los registros que se importaron correctamente no se duplicarán en la segunda importación.

### Actualizar Datos Existentes

Para actualizar datos de participantes ya importados:

1. Modifica los datos en el archivo Excel
2. Mantén el mismo DNI y Nombre del Evento
3. Importa el archivo nuevamente
4. El sistema actualizará automáticamente los registros existentes

## Gestión de Participantes

### Ver Lista de Participantes

1. Haz clic en **"Participants"** en el menú principal
2. Verás una tabla con:
   - DNI
   - Nombre completo
   - Evento
   - Tipo de asistente
   - Fecha de registro

### Buscar Participantes

En la lista de participantes:

1. Usa la barra de búsqueda
2. Puedes buscar por:
   - DNI
   - Nombre completo
   - Nombre del evento

**Ejemplos:**
- Buscar por DNI: `12345678`
- Buscar por nombre: `Juan Pérez`
- Buscar por evento: `Seguridad Vial`

### Filtrar Participantes

Usa los filtros del panel derecho:

- **Por tipo de asistente**: Asistente, Ponente, Organizador
- **Por evento**: Filtra por evento específico
- **Por fecha de registro**: Hoy, últimos 7 días, este mes

### Editar un Participante

1. Haz clic en el participante que deseas editar
2. Modifica los campos necesarios:
   - DNI
   - Nombre completo
   - Tipo de asistente
3. Haz clic en **"Save"**

⚠️ **Importante:** Si el participante ya tiene un certificado generado y modificas sus datos, deberás:
1. Eliminar el certificado existente
2. Regenerar el certificado con los datos actualizados

### Eliminar un Participante

⚠️ **Advertencia:** Eliminar un participante también eliminará su certificado asociado.

1. En la lista de participantes, marca el checkbox del participante
2. En el menú desplegable de acciones, selecciona **"Delete selected participants"**
3. Haz clic en **"Go"**
4. Confirma la eliminación

### Ver Certificado de un Participante

1. En la lista de participantes, haz clic en el participante
2. En la página de detalles, verás:
   - Datos del participante
   - Enlace al certificado (si existe)
3. Haz clic en el enlace del certificado para descargarlo

## Generación de Certificados

### Generar Certificados para un Evento

**Método 1: Desde la lista de eventos**

1. Ve a **"Events"**
2. Marca el checkbox del evento
3. Selecciona la acción **"Generar Certificados"**
4. Haz clic en **"Go"**

**Método 2: Usando comando de management**

```bash
python manage.py generate_certificates --event-id 1
```

### Verificar Certificados Generados

1. Ve a **"Certificates"**
2. Filtra por el evento deseado
3. Verás la lista de certificados generados con:
   - UUID único
   - Participante
   - Evento
   - Fecha de generación
   - Estado de firma

### Descargar un Certificado

**Desde la lista de certificados:**

1. Haz clic en el certificado
2. En la página de detalles, haz clic en el enlace del archivo PDF
3. El certificado se descargará

**Desde la lista de participantes:**

1. Haz clic en el participante
2. Haz clic en el enlace del certificado
3. El certificado se descargará

### Regenerar un Certificado

Si necesitas regenerar un certificado (por ejemplo, después de editar datos):

1. Ve a **"Certificates"**
2. Encuentra el certificado a regenerar
3. Marca el checkbox
4. Selecciona la acción **"Delete selected certificates"**
5. Haz clic en **"Go"** y confirma
6. Ve a **"Events"**
7. Genera nuevamente los certificados para ese evento

### Descargar Múltiples Certificados

**Opción 1: Descarga individual**
- Descarga cada certificado uno por uno

**Opción 2: Acceso directo a archivos**
- Los certificados se guardan en: `media/certificates/YYYY/MM/`
- Puedes acceder directamente a la carpeta y copiar múltiples archivos

**Opción 3: Usar comando de management (avanzado)**
```bash
# Crear un ZIP con todos los certificados de un evento
# (requiere script personalizado)
```

## Firma Digital de Certificados

### Requisitos Previos

Antes de firmar certificados, asegúrate de que:

1. ✅ Los certificados estén generados
2. ✅ El servicio de firma digital esté configurado
3. ✅ Tengas una API Key válida

Ver [Configuración del Servicio de Firma Digital](../README.md#configuración-del-servicio-de-firma-digital) para detalles.

### Firmar Certificados de un Evento

**Método 1: Desde el panel de administración**

1. Ve a **"Certificates"**
2. Filtra por el evento deseado
3. Filtra por "No firmados" (is_signed = No)
4. Marca los checkboxes de los certificados a firmar
5. En el menú de acciones, selecciona **"Firmar Certificados"**
6. Haz clic en **"Go"**
7. El sistema enviará los certificados al servicio de firma
8. Verás un mensaje con el resultado:
   ```
   ✅ Se firmaron 42 certificados exitosamente
   ❌ 3 certificados fallaron (ver logs para detalles)
   ```

**Método 2: Usando comando de management**

```bash
# Firmar certificados de un evento específico
python manage.py sign_certificates --event-id 1

# Firmar todos los certificados pendientes
python manage.py sign_certificates --all

# Reintentar certificados que fallaron
python manage.py sign_certificates --event-id 1 --retry-failed
```

### Verificar Estado de Firma

1. Ve a **"Certificates"**
2. En la lista, verás la columna **"Is signed"**:
   - ✅ (checkmark verde): Certificado firmado
   - ❌ (X roja): Certificado no firmado
3. Haz clic en un certificado para ver detalles:
   - Fecha de firma
   - Estado de firma

### Solucionar Problemas de Firma

Si la firma falla:

1. **Verifica la configuración**
   ```bash
   # Verifica las variables de entorno
   echo $SIGNATURE_SERVICE_URL
   echo $SIGNATURE_API_KEY
   ```

2. **Revisa los logs**
   ```bash
   # Windows
   type logs\signature.log
   
   # Linux/Mac
   tail -f logs/signature.log
   ```

3. **Reintenta la firma**
   - El sistema reintenta automáticamente 3 veces
   - Puedes reintentar manualmente usando el comando con `--retry-failed`

4. **Contacta al proveedor del servicio**
   - Si el problema persiste, contacta al soporte del servicio de firma digital

## Gestión de Plantillas

### Ver Plantillas Disponibles

1. Haz clic en **"Certificate Templates"** en el menú principal
2. Verás la lista de plantillas con:
   - Nombre
   - Si es plantilla por defecto
   - Fecha de creación

### Usar la Plantilla por Defecto

El sistema incluye una plantilla por defecto llamada "Plantilla DRTC Puno".

Esta plantilla se carga automáticamente al instalar el sistema con:
```bash
python manage.py load_default_template
```

### Crear una Nueva Plantilla

⚠️ **Nota:** La creación de plantillas requiere conocimientos de HTML/CSS. Consulta con el equipo técnico.

1. Haz clic en **"Add Certificate Template"**
2. Completa los campos:
   - **Name**: Nombre descriptivo
   - **HTML Template**: Código HTML de la plantilla
   - **CSS Styles**: Estilos CSS personalizados
   - **Background Image**: Imagen de fondo (opcional)
   - **Is Default**: Marca si será la plantilla por defecto
   - **Field Positions**: JSON con posiciones de campos (avanzado)
3. Haz clic en **"Save"**

### Establecer Plantilla por Defecto

1. Ve a **"Certificate Templates"**
2. Haz clic en la plantilla que deseas establecer como predeterminada
3. Marca el checkbox **"Is default"**
4. Haz clic en **"Save"**

**Nota:** Solo puede haber una plantilla por defecto. Si marcas otra como predeterminada, la anterior se desmarcará automáticamente.

### Asignar Plantilla a un Evento

1. Ve a **"Events"**
2. Haz clic en el evento
3. En el campo **"Template"**, selecciona la plantilla deseada
4. Haz clic en **"Save"**

## Auditoría y Logs

### Ver Registro de Auditoría

1. Haz clic en **"Audit Logs"** en el menú principal
2. Verás una tabla con todas las acciones registradas:
   - Tipo de acción
   - Usuario
   - Descripción
   - Fecha y hora
   - Dirección IP (para acciones públicas)

### Tipos de Acciones Registradas

- **IMPORT**: Importación de participantes desde Excel
- **GENERATE**: Generación de certificados
- **SIGN**: Firma digital de certificados
- **QUERY**: Consulta pública por DNI
- **VERIFY**: Verificación de certificado por QR

### Filtrar Logs

Usa los filtros del panel derecho:

- **Por tipo de acción**: Filtra por tipo específico
- **Por usuario**: Filtra por usuario que realizó la acción
- **Por fecha**: Hoy, últimos 7 días, este mes, este año

### Buscar en Logs

Usa la barra de búsqueda para buscar por:
- Descripción de la acción
- Metadata

### Ver Detalles de un Log

1. Haz clic en un registro de log
2. Verás información detallada:
   - Tipo de acción
   - Usuario que la realizó
   - Descripción completa
   - Metadata (JSON con información adicional)
   - Dirección IP
   - Fecha y hora exacta

### Exportar Logs

Para exportar logs (requiere acceso a la base de datos):

```bash
# Exportar logs a CSV
python manage.py dumpdata certificates.AuditLog --format=json > audit_logs.json
```

## Flujo de Trabajo Completo

### Proceso Estándar para un Nuevo Evento

Sigue estos pasos para gestionar un evento completo:

#### 1. Crear el Evento (5 minutos)

1. Ve a **"Events"** → **"Add Event"**
2. Completa:
   - Nombre: "Capacitación en Seguridad Vial 2024"
   - Fecha: 15/10/2024
   - Descripción: (opcional)
   - Plantilla: "Plantilla DRTC Puno"
3. Guarda

#### 2. Preparar Lista de Participantes (15-30 minutos)

1. Descarga la plantilla de Excel
2. Completa con los datos de los participantes:
   - DNI
   - Nombres y Apellidos
   - Fecha del Evento
   - Tipo de Asistente
   - Nombre del Evento
3. Verifica que todos los datos sean correctos

#### 3. Importar Participantes (2-5 minutos)

1. Ve a **"Import Excel"**
2. Selecciona tu archivo Excel
3. Haz clic en **"Import"**
4. Verifica el reporte de importación
5. Si hay errores, corrígelos y vuelve a importar

#### 4. Verificar Participantes (5 minutos)

1. Ve a **"Participants"**
2. Filtra por el evento
3. Verifica que todos los participantes estén correctos
4. Corrige cualquier error si es necesario

#### 5. Generar Certificados (5-10 minutos)

1. Ve a **"Events"**
2. Selecciona el evento
3. Acción: **"Generar Certificados"**
4. Espera la confirmación
5. Verifica que se generaron todos los certificados

#### 6. Revisar Certificados (10 minutos)

1. Ve a **"Certificates"**
2. Filtra por el evento
3. Descarga y revisa algunos certificados de muestra
4. Verifica que los datos sean correctos
5. Verifica que el código QR esté presente

#### 7. Firmar Certificados (10-30 minutos)

1. Ve a **"Certificates"**
2. Filtra por el evento y "No firmados"
3. Selecciona todos los certificados
4. Acción: **"Firmar Certificados"**
5. Espera la confirmación
6. Verifica el resultado

#### 8. Verificación Final (5 minutos)

1. Descarga algunos certificados firmados
2. Verifica que tengan la firma digital
3. Escanea un código QR para verificar que funcione
4. Confirma que todo esté correcto

#### 9. Distribución (variable)

1. Notifica a los participantes que pueden consultar sus certificados
2. Proporciona la URL: `https://certificados.drtcpuno.gob.pe/consulta/`
3. Indica que deben ingresar su DNI

**Tiempo total estimado:** 1-2 horas (dependiendo del número de participantes)

## Mejores Prácticas

### Organización de Eventos

1. **Nombres descriptivos**
   - Usa nombres claros y únicos para cada evento
   - Incluye el año si es un evento recurrente
   - Ejemplo: "Capacitación en Seguridad Vial 2024" en lugar de "Capacitación 1"

2. **Documentación**
   - Mantén una copia del archivo Excel original
   - Documenta cualquier cambio o corrección realizada
   - Guarda los reportes de importación

3. **Verificación**
   - Siempre verifica los datos antes de generar certificados
   - Revisa algunos certificados de muestra antes de firmar todos
   - Prueba el código QR de al menos un certificado

### Seguridad

1. **Contraseñas**
   - Usa contraseñas fuertes
   - Cambia tu contraseña regularmente
   - No compartas tu contraseña

2. **Sesiones**
   - Cierra sesión cuando termines
   - No dejes la sesión abierta en computadoras compartidas

3. **Datos sensibles**
   - No compartas archivos Excel con datos de participantes
   - Elimina archivos temporales después de importar
   - Respeta la privacidad de los participantes

### Respaldo

1. **Archivos Excel**
   - Mantén copias de seguridad de todos los archivos Excel
   - Organiza por fecha y evento
   - Guarda en ubicación segura

2. **Certificados**
   - El sistema hace respaldo automático
   - Verifica que los respaldos se estén realizando
   - Contacta al administrador del sistema para restaurar si es necesario

### Eficiencia

1. **Importación por lotes**
   - Para eventos grandes, importa en lotes de 500-1000 participantes
   - Verifica cada lote antes de continuar

2. **Generación programada**
   - Genera certificados en horarios de baja actividad
   - La firma digital puede tomar tiempo para eventos grandes

3. **Uso de filtros**
   - Usa filtros para encontrar rápidamente lo que buscas
   - Guarda búsquedas frecuentes (marcadores del navegador)

## Solución de Problemas

### No puedo iniciar sesión

**Problema:** Mensaje "Please enter a correct username and password"

**Soluciones:**
1. Verifica que el usuario y contraseña sean correctos
2. Verifica que las mayúsculas estén correctas
3. Contacta al administrador para restablecer tu contraseña

### Error al importar Excel

**Problema:** "Invalid file format" o "Missing columns"

**Soluciones:**
1. Verifica que el archivo sea .xlsx o .xls
2. Verifica que las columnas tengan los nombres exactos
3. Descarga la plantilla y copia tus datos allí
4. Ver [Formato del Archivo Excel](EXCEL_FORMAT.md)

### Certificados no se generan

**Problema:** Acción "Generar Certificados" no funciona

**Soluciones:**
1. Verifica que el evento tenga participantes
2. Verifica que haya una plantilla asignada al evento
3. Revisa los logs: `logs/certificates.log`
4. Contacta al administrador del sistema

### Firma digital falla

**Problema:** Error al firmar certificados

**Soluciones:**
1. Verifica la configuración del servicio de firma
2. Revisa los logs: `logs/signature.log`
3. Reintenta la firma
4. Contacta al proveedor del servicio de firma

### Certificado no se descarga

**Problema:** 404 o error al descargar certificado

**Soluciones:**
1. Verifica que el certificado esté generado
2. Actualiza la página
3. Intenta desde otro navegador
4. Contacta al administrador del sistema

### Código QR no funciona

**Problema:** Al escanear el QR no se abre la página de verificación

**Soluciones:**
1. Verifica que el certificado esté generado correctamente
2. Verifica que el código QR sea legible
3. Intenta escanear con otra aplicación
4. Copia la URL manualmente y ábrela en el navegador

## Contacto y Soporte

### Soporte Técnico

- **Email**: soporte@drtcpuno.gob.pe
- **Teléfono**: (051) XXX-XXXX
- **Horario**: Lunes a Viernes, 8:00 AM - 5:00 PM

### Reportar Problemas

Al reportar un problema, incluye:

1. Descripción clara del problema
2. Pasos para reproducir
3. Capturas de pantalla (si aplica)
4. Mensajes de error exactos
5. Navegador y versión que usas

### Solicitar Nuevas Funcionalidades

Si tienes sugerencias para mejorar el sistema:

1. Describe la funcionalidad deseada
2. Explica el caso de uso
3. Indica la prioridad
4. Envía a: soporte@drtcpuno.gob.pe

---

**Última actualización:** 28 de octubre de 2024
