# Requirements Document

## Introduction

Este documento define los requisitos para el Sistema de Certificados de Capacitaciones de la Dirección Regional de Transportes y Comunicaciones Puno. El sistema permitirá gestionar certificados de eventos de capacitación, importar participantes desde Excel, generar certificados PDF con códigos QR de verificación, consultar certificados por DNI, y enviar certificados para firma digital mediante un servicio REST externo.

## Requirements

### Requirement 1: Importación de Participantes desde Excel

**User Story:** Como administrador del sistema, quiero importar la lista de participantes desde un archivo Excel, para que pueda registrar masivamente a los asistentes, ponentes y organizadores de un evento de capacitación.

#### Acceptance Criteria

1. WHEN el administrador selecciona un archivo Excel THEN el sistema SHALL validar que el archivo contenga las columnas requeridas: DNI, Nombres y Apellidos, Fecha del Evento, Tipo de Asistente, y Nombre del Evento
2. WHEN el archivo Excel es válido THEN el sistema SHALL procesar cada fila y crear registros de participantes en la base de datos
3. WHEN se procesa una fila con DNI duplicado para el mismo evento THEN el sistema SHALL actualizar el registro existente en lugar de crear uno nuevo
4. WHEN el campo "Tipo de Asistente" contiene un valor THEN el sistema SHALL validar que sea uno de los valores permitidos: ASISTENTE, PONENTE, u ORGANIZADOR
5. WHEN la importación se completa THEN el sistema SHALL mostrar un resumen con el número de registros importados exitosamente y los errores encontrados
6. WHEN hay errores en el archivo THEN el sistema SHALL generar un reporte detallado indicando las filas con problemas y la razón del error
7. IF el formato de fecha es inválido THEN el sistema SHALL rechazar esa fila y registrar el error

### Requirement 2: Generación de Certificados con Código QR

**User Story:** Como administrador del sistema, quiero generar certificados PDF desde una plantilla prediseñada con códigos QR únicos, para que cada participante tenga un certificado verificable y personalizado.

#### Acceptance Criteria

1. WHEN se solicita generar certificados para un evento THEN el sistema SHALL crear un certificado PDF para cada participante registrado en ese evento
2. WHEN se genera un certificado THEN el sistema SHALL utilizar una plantilla prediseñada que incluya los datos del participante: DNI, Nombres y Apellidos, Nombre del Evento, Fecha del Evento, y Tipo de Asistente
3. WHEN se crea un certificado THEN el sistema SHALL generar un código QR único que contenga la URL de verificación del certificado
4. WHEN se genera el código QR THEN el sistema SHALL incluir en la URL un identificador único del certificado que permita su verificación posterior
5. WHEN el certificado se genera exitosamente THEN el sistema SHALL almacenar el archivo PDF y asociarlo con el registro del participante
6. WHEN se genera un certificado THEN el sistema SHALL registrar la fecha y hora de generación
7. IF ya existe un certificado generado para un participante THEN el sistema SHALL permitir regenerarlo manteniendo el mismo identificador único

### Requirement 3: Consulta de Certificados por DNI

**User Story:** Como participante de un evento, quiero consultar mis certificados ingresando únicamente mi DNI en una página web, para que pueda acceder y descargar mis certificados de manera fácil y rápida.

#### Acceptance Criteria

1. WHEN el usuario accede a la página de consulta THEN el sistema SHALL mostrar un formulario solicitando únicamente el número de DNI
2. WHEN el usuario ingresa un DNI y envía el formulario THEN el sistema SHALL buscar todos los certificados asociados a ese DNI
3. WHEN se encuentran certificados THEN el sistema SHALL mostrar una lista con: Nombre del Evento, Fecha del Evento, Tipo de Asistente, y un botón para descargar el PDF
4. WHEN no se encuentran certificados para el DNI ingresado THEN el sistema SHALL mostrar un mensaje indicando que no hay certificados registrados
5. WHEN el usuario hace clic en descargar THEN el sistema SHALL permitir la descarga del archivo PDF del certificado
6. WHEN se muestra la lista de certificados THEN el sistema SHALL ordenarlos por fecha del evento de manera descendente (más recientes primero)
7. IF el DNI ingresado tiene un formato inválido THEN el sistema SHALL mostrar un mensaje de error de validación

### Requirement 4: Verificación de Certificados mediante Código QR

**User Story:** Como verificador externo, quiero escanear el código QR de un certificado y acceder a una página de verificación, para que pueda confirmar la autenticidad del certificado.

#### Acceptance Criteria

1. WHEN se escanea el código QR de un certificado THEN el sistema SHALL redirigir a una URL de verificación única
2. WHEN se accede a la URL de verificación THEN el sistema SHALL buscar el certificado correspondiente al identificador único
3. WHEN el certificado existe THEN el sistema SHALL mostrar los datos del certificado: DNI, Nombres y Apellidos, Nombre del Evento, Fecha del Evento, Tipo de Asistente, y estado de firma digital
4. WHEN el certificado no existe THEN el sistema SHALL mostrar un mensaje indicando que el certificado no es válido o no se encuentra en el sistema
5. WHEN se muestra la información del certificado THEN el sistema SHALL indicar claramente si el certificado ha sido firmado digitalmente
6. WHEN el certificado ha sido firmado THEN el sistema SHALL mostrar la fecha de firma digital

### Requirement 5: Envío de Certificados para Firma Digital

**User Story:** Como administrador del sistema, quiero enviar los certificados PDF a un servicio REST externo para que sean firmados digitalmente, para que los certificados tengan validez legal y autenticidad verificable.

#### Acceptance Criteria

1. WHEN el administrador selecciona certificados para firmar THEN el sistema SHALL permitir seleccionar uno o múltiples certificados generados
2. WHEN se solicita la firma digital THEN el sistema SHALL enviar el archivo PDF al servicio REST externo mediante una petición HTTP
3. WHEN se envía el PDF al servicio REST THEN el sistema SHALL incluir los metadatos necesarios según la especificación del servicio externo
4. WHEN el servicio REST responde exitosamente THEN el sistema SHALL recibir el PDF firmado y reemplazar el archivo original
5. WHEN se recibe el PDF firmado THEN el sistema SHALL actualizar el estado del certificado indicando que ha sido firmado digitalmente y registrar la fecha de firma
6. WHEN el servicio REST falla THEN el sistema SHALL registrar el error y permitir reintentar el envío posteriormente
7. IF un certificado ya está firmado THEN el sistema SHALL prevenir que sea enviado nuevamente para firma
8. WHEN se completa el proceso de firma THEN el sistema SHALL notificar al administrador del resultado (éxito o error)

### Requirement 6: Gestión de Plantillas de Certificados

**User Story:** Como administrador del sistema, quiero configurar y gestionar plantillas de certificados, para que pueda personalizar el diseño según el tipo de evento o capacitación.

#### Acceptance Criteria

1. WHEN el administrador accede a la gestión de plantillas THEN el sistema SHALL mostrar las plantillas disponibles
2. WHEN se crea una plantilla THEN el sistema SHALL permitir definir el diseño mediante un archivo HTML/CSS o imagen de fondo
3. WHEN se define una plantilla THEN el sistema SHALL permitir especificar las posiciones donde se insertarán los datos variables (nombre, DNI, fecha, etc.)
4. WHEN se guarda una plantilla THEN el sistema SHALL validar que todos los campos requeridos estén configurados
5. WHEN se genera un certificado THEN el sistema SHALL utilizar la plantilla asociada al tipo de evento o la plantilla por defecto
6. IF no existe una plantilla configurada THEN el sistema SHALL utilizar una plantilla predeterminada del sistema

### Requirement 7: Panel de Administración

**User Story:** Como administrador del sistema, quiero acceder a un panel de administración con autenticación, para que pueda gestionar eventos, participantes, certificados y configuraciones del sistema de manera segura.

#### Acceptance Criteria

1. WHEN el administrador accede al sistema THEN el sistema SHALL solicitar credenciales de autenticación (usuario y contraseña)
2. WHEN las credenciales son válidas THEN el sistema SHALL permitir acceso al panel de administración
3. WHEN el administrador está autenticado THEN el sistema SHALL mostrar un menú con las opciones: Eventos, Participantes, Certificados, Importar Excel, Plantillas, y Configuración
4. WHEN se accede a la sección de Eventos THEN el sistema SHALL permitir crear, editar, listar y eliminar eventos de capacitación
5. WHEN se accede a la sección de Participantes THEN el sistema SHALL permitir ver, buscar y editar participantes registrados
6. WHEN se accede a la sección de Certificados THEN el sistema SHALL permitir generar, regenerar, descargar y enviar certificados para firma
7. IF el usuario no está autenticado THEN el sistema SHALL redirigir a la página de login al intentar acceder a cualquier función administrativa

### Requirement 8: Registro de Auditoría

**User Story:** Como administrador del sistema, quiero que el sistema registre todas las acciones importantes realizadas, para que pueda auditar y rastrear cambios en certificados y participantes.

#### Acceptance Criteria

1. WHEN se importa un archivo Excel THEN el sistema SHALL registrar quién realizó la importación, cuándo, y cuántos registros se procesaron
2. WHEN se genera un certificado THEN el sistema SHALL registrar quién lo generó y cuándo
3. WHEN se envía un certificado para firma digital THEN el sistema SHALL registrar el evento, el resultado y la fecha
4. WHEN se consulta un certificado por DNI THEN el sistema SHALL registrar la consulta con fecha y hora
5. WHEN se verifica un certificado mediante QR THEN el sistema SHALL registrar la verificación
6. WHEN el administrador accede al registro de auditoría THEN el sistema SHALL mostrar un listado filtrable y ordenable de todas las acciones registradas
