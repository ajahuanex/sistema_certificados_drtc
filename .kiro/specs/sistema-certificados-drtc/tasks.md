# Implementation Plan

- [x] 1. Configurar proyecto Django y estructura base






  - Crear proyecto Django con estructura de settings modular (base, development, production)
  - Configurar PostgreSQL como base de datos
  - Instalar y configurar dependencias iniciales (Django, psycopg2, django-environ)
  - Crear aplicación 'certificates' dentro del proyecto
  - Configurar archivos estáticos y media
  - _Requirements: 7.1, 7.2_

- [x] 2. Implementar modelos de datos



  - [x] 2.1 Crear modelo Event


    - Escribir clase Event con campos: name, event_date, description, template, created_at, updated_at
    - Implementar método __str__ para representación legible
    - Crear y ejecutar migración
    - _Requirements: 1.1, 2.1_
  
  - [x] 2.2 Crear modelo Participant


    - Escribir clase Participant con campos: dni, full_name, event, attendee_type, created_at
    - Implementar validación de DNI (8 dígitos)
    - Configurar unique_together para (dni, event)
    - Crear índices en dni y (dni, event)
    - Implementar método __str__
    - Crear y ejecutar migración
    - _Requirements: 1.1, 1.2, 1.3_
  
  - [x] 2.3 Crear modelo Certificate


    - Escribir clase Certificate con campos: uuid, participant, pdf_file, qr_code, generated_at, is_signed, signed_at, verification_url
    - Configurar UUID como campo único no editable
    - Implementar relación OneToOne con Participant
    - Configurar upload_to para archivos con estructura de carpetas por fecha
    - Implementar método __str__
    - Crear y ejecutar migración
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 4.1_
  
  - [x] 2.4 Crear modelo CertificateTemplate

    - Escribir clase CertificateTemplate con campos: name, html_template, css_styles, background_image, is_default, field_positions
    - Implementar validación para asegurar solo una plantilla por defecto
    - Implementar método __str__
    - Crear y ejecutar migración
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [x] 2.5 Crear modelo AuditLog


    - Escribir clase AuditLog con campos: action_type, user, description, metadata, ip_address, timestamp
    - Configurar choices para action_type
    - Crear índices en timestamp y action_type
    - Implementar método __str__
    - Crear y ejecutar migración
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 3. Implementar servicio de procesamiento de Excel



  - [x] 3.1 Crear ExcelProcessorService básico

    - Crear archivo services/excel_processor.py
    - Implementar clase ExcelProcessorService con constante REQUIRED_COLUMNS
    - Implementar método validate_file() que verifica columnas requeridas
    - Escribir tests unitarios para validate_file()
    - _Requirements: 1.1_
  
  - [x] 3.2 Implementar parseo y validación de filas


    - Implementar método _parse_row() que extrae datos de una fila Excel
    - Implementar método _validate_row() que valida DNI, fecha, tipo de asistente
    - Implementar validación de formato de DNI (8 dígitos numéricos)
    - Implementar validación de tipo de asistente (ASISTENTE, PONENTE, ORGANIZADOR)
    - Escribir tests unitarios para _parse_row() y _validate_row()
    - _Requirements: 1.1, 1.4, 1.7_
  
  - [x] 3.3 Implementar creación/actualización de participantes


    - Implementar método _create_or_update_participant() que crea o actualiza Event y Participant
    - Manejar lógica de get_or_create para Event basado en nombre y fecha
    - Manejar lógica de update_or_create para Participant basado en DNI y evento
    - Escribir tests unitarios para _create_or_update_participant()
    - _Requirements: 1.2, 1.3_
  
  - [x] 3.4 Implementar proceso completo de importación


    - Implementar método process_excel() que procesa archivo completo
    - Iterar sobre filas, validar y crear participantes
    - Recolectar errores y éxitos en estructuras de datos
    - Generar diccionario de resultado con success_count, error_count, errors
    - Registrar importación en AuditLog
    - Escribir tests de integración para process_excel()
    - _Requirements: 1.2, 1.5, 1.6, 8.1_

- [x] 4. Implementar servicio de generación de códigos QR



  - Crear archivo services/qr_service.py
  - Implementar clase QRCodeService
  - Implementar método get_verification_url() que genera URL con UUID
  - Implementar método generate_qr() que crea imagen QR usando librería qrcode
  - Configurar tamaño y formato del QR (PNG, 300x300px)
  - Escribir tests unitarios para QRCodeService
  - _Requirements: 2.3, 2.4, 4.1, 4.4_

- [x] 5. Implementar servicio de generación de certificados


  - [x] 5.1 Crear CertificateGeneratorService básico


    - Crear archivo services/certificate_generator.py
    - Implementar clase CertificateGeneratorService
    - Inyectar dependencia de QRCodeService
    - Escribir estructura básica de métodos
    - _Requirements: 2.1_
  
  - [x] 5.2 Implementar renderizado de plantillas


    - Implementar método _render_template() que renderiza HTML con datos del participante
    - Usar Django template engine para reemplazar variables
    - Manejar plantilla por defecto si no existe plantilla específica
    - Escribir tests unitarios para _render_template()
    - _Requirements: 2.2, 6.5, 6.6_
  
  - [x] 5.3 Implementar generación de PDF


    - Implementar método _create_pdf() que convierte HTML a PDF usando WeasyPrint
    - Integrar código QR en el PDF
    - Configurar tamaño de página y márgenes
    - Manejar CSS y estilos de la plantilla
    - Escribir tests unitarios para _create_pdf()
    - _Requirements: 2.2, 2.3_
  
  - [x] 5.4 Implementar generación de certificado completo


    - Implementar método generate_certificate() que orquesta todo el proceso
    - Generar URL de verificación usando QRCodeService
    - Renderizar plantilla con datos del participante
    - Generar código QR
    - Crear PDF
    - Guardar archivos en storage (pdf_file y qr_code)
    - Crear registro de Certificate en base de datos
    - Registrar generación en AuditLog
    - Escribir tests de integración para generate_certificate()
    - _Requirements: 2.1, 2.2, 2.3, 2.5, 2.6, 8.2_
  
  - [x] 5.5 Implementar generación masiva de certificados


    - Implementar método generate_bulk_certificates() que genera certificados para todos los participantes de un evento
    - Iterar sobre participantes del evento
    - Llamar a generate_certificate() para cada uno
    - Recolectar resultados y errores
    - Retornar lista de certificados generados
    - Escribir tests para generate_bulk_certificates()
    - _Requirements: 2.1, 2.7_

- [x] 6. Implementar servicio de firma digital


  - [x] 6.1 Crear DigitalSignatureService básico


    - Crear archivo services/digital_signature.py
    - Implementar clase DigitalSignatureService
    - Configurar constantes MAX_RETRIES y RETRY_DELAY
    - Cargar configuración de URL y API key desde settings
    - _Requirements: 5.1, 5.2_
  
  - [x] 6.2 Implementar comunicación con servicio externo


    - Implementar método _send_to_signature_service() que envía PDF al servicio REST
    - Configurar headers con autenticación (Bearer token)
    - Leer archivo PDF y enviarlo en el body de la petición
    - Configurar timeout de 30 segundos
    - Manejar respuesta y extraer PDF firmado
    - Escribir tests con mock del servicio externo
    - _Requirements: 5.2, 5.3_
  
  - [x] 6.3 Implementar lógica de reintentos


    - Implementar método sign_certificate() con lógica de reintentos
    - Manejar excepciones de timeout y HTTP errors
    - Implementar delay entre reintentos
    - Registrar intentos en logs
    - Escribir tests para lógica de reintentos
    - _Requirements: 5.6_
  
  - [x] 6.4 Implementar actualización de estado del certificado


    - Implementar método _update_certificate_status() que actualiza Certificate
    - Reemplazar pdf_file con PDF firmado
    - Actualizar is_signed a True
    - Establecer signed_at con timestamp actual
    - Registrar firma en AuditLog
    - Validar que certificado no esté ya firmado antes de enviar
    - Escribir tests para _update_certificate_status()
    - _Requirements: 5.4, 5.5, 5.7, 8.3_
  
  - [x] 6.5 Implementar firma masiva de certificados


    - Implementar método sign_bulk_certificates() que firma múltiples certificados
    - Iterar sobre lista de certificados
    - Llamar a sign_certificate() para cada uno
    - Recolectar resultados (éxitos y errores)
    - Retornar diccionario con estadísticas
    - Notificar resultado al administrador
    - Escribir tests para sign_bulk_certificates()
    - _Requirements: 5.1, 5.8_

- [x] 7. Implementar formularios



  - Crear archivo forms.py en la aplicación certificates
  - Implementar ExcelImportForm con FileField y validación de extensión (.xlsx, .xls)
  - Implementar método clean_excel_file() para validar tamaño máximo (10MB)
  - Implementar DNIQueryForm con CharField y validación de 8 dígitos
  - Escribir tests unitarios para ambos formularios
  - _Requirements: 1.1, 3.7_

- [x] 8. Implementar vistas de administración


  - [x] 8.1 Configurar Django Admin para modelos



    - Crear archivo admin.py
    - Registrar EventAdmin con list_display, search_fields, list_filter
    - Registrar ParticipantAdmin con list_display, search_fields, list_filter
    - Registrar CertificateAdmin con list_display, search_fields, list_filter
    - Registrar CertificateTemplateAdmin con list_display
    - Registrar AuditLogAdmin como solo lectura
    - _Requirements: 7.3, 7.4, 7.5_
  
  - [x] 8.2 Implementar vista de importación Excel



    - Crear archivo views/admin_views.py
    - Implementar ExcelImportView basada en FormView
    - Implementar método form_valid() que llama a ExcelProcessorService
    - Mostrar mensajes de éxito o error usando Django messages
    - Renderizar template con formulario de carga
    - Agregar decorador @staff_member_required
    - Escribir tests para ExcelImportView
    - _Requirements: 1.1, 1.5, 1.6_
  
  - [x] 8.3 Implementar acciones admin personalizadas


    - Agregar acción "Generar Certificados" en EventAdmin
    - Implementar método que llama a CertificateGeneratorService.generate_bulk_certificates()
    - Agregar acción "Firmar Certificados" en CertificateAdmin
    - Implementar método que llama a DigitalSignatureService.sign_bulk_certificates()
    - Agregar acción "Descargar PDF" en CertificateAdmin
    - Mostrar mensajes de resultado de las acciones
    - Escribir tests para acciones admin
    - _Requirements: 2.1, 5.1, 7.3_

- [x] 9. Implementar vistas públicas




  - [x] 9.1 Implementar vista de consulta por DNI


    - Crear archivo views/public_views.py
    - Implementar CertificateQueryView basada en TemplateView
    - Implementar método get() que muestra formulario DNIQueryForm
    - Implementar método post() que busca certificados por DNI
    - Filtrar Certificate por participant__dni
    - Usar select_related para optimizar query
    - Ordenar resultados por fecha descendente
    - Renderizar template con lista de certificados o mensaje si no hay resultados
    - Registrar consulta en AuditLog con IP del usuario
    - Escribir tests para CertificateQueryView
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6, 3.7, 8.4_
  
  - [x] 9.2 Implementar vista de descarga de certificado

    - Implementar CertificateDownloadView que retorna FileResponse
    - Buscar Certificate por UUID
    - Retornar pdf_file como descarga
    - Configurar Content-Disposition header para descarga
    - Manejar caso de certificado no encontrado (404)
    - Escribir tests para CertificateDownloadView
    - _Requirements: 3.5_
  
  - [x] 9.3 Implementar vista de verificación por QR

    - Implementar CertificateVerificationView basada en DetailView
    - Buscar Certificate por UUID en la URL
    - Renderizar template con datos del certificado
    - Mostrar: DNI, nombre completo, evento, fecha, tipo de asistente, estado de firma
    - Mostrar mensaje si certificado no existe
    - Registrar verificación en AuditLog
    - Escribir tests para CertificateVerificationView
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 8.5_

- [x] 10. Implementar templates HTML






  - [x] 10.1 Crear template base

    - Crear templates/base.html con estructura HTML5
    - Incluir Bootstrap 5 CSS
    - Definir bloques: title, extra_css, content, extra_js
    - Crear navbar con logo de DRTC Puno
    - Crear footer con información de contacto
    - _Requirements: 3.1, 4.1_
  

  - [x] 10.2 Crear templates de administración

    - Crear templates/admin/excel_import.html con formulario de carga
    - Mostrar instrucciones sobre formato del Excel
    - Mostrar tabla de resultados de importación si existe
    - Aplicar estilos de Django Admin
    - _Requirements: 1.1, 1.5_
  

  - [x] 10.3 Crear templates públicos

    - Crear templates/certificates/query.html con formulario de consulta DNI
    - Crear templates/certificates/results.html con lista de certificados
    - Mostrar tabla con: evento, fecha, tipo, botón de descarga
    - Crear templates/certificates/verify.html con datos del certificado verificado
    - Mostrar badge de "Firmado Digitalmente" si aplica
    - Aplicar diseño responsive con Bootstrap
    - _Requirements: 3.1, 3.3, 4.3, 4.5_

- [x] 11. Configurar URLs





  - Crear archivo urls.py en la aplicación certificates
  - Configurar ruta para admin: /admin/
  - Configurar ruta para importación: /admin/import-excel/
  - Configurar ruta para consulta pública: /consulta/
  - Configurar ruta para descarga: /certificado/<uuid>/descargar/
  - Configurar ruta para verificación: /verificar/<uuid>/
  - Incluir URLs de certificates en el proyecto principal
  - Configurar serving de archivos media en desarrollo
  - Escribir tests para todas las URLs
  - _Requirements: 3.1, 3.5, 4.1_

- [x] 12. Crear plantilla de certificado por defecto





  - Crear archivo templates/certificates/default_certificate.html
  - Diseñar layout con logo de DRTC Puno
  - Definir posiciones para: nombre completo, DNI, evento, fecha, tipo de asistente
  - Incluir espacio para código QR
  - Crear CSS para estilos de impresión
  - Configurar tamaño A4 horizontal
  - Crear comando de management para cargar plantilla por defecto en DB
  - _Requirements: 2.2, 6.6_

- [x] 13. Implementar configuración de settings





  - [x] 13.1 Configurar settings base


    - Crear settings/base.py con configuración común
    - Configurar INSTALLED_APPS incluyendo certificates
    - Configurar MIDDLEWARE
    - Configurar TEMPLATES con directorio de templates
    - Configurar STATIC_URL y MEDIA_URL
    - Configurar internacionalización (es-PE)
    - _Requirements: 7.1_
  
  - [x] 13.2 Configurar settings de desarrollo


    - Crear settings/development.py heredando de base
    - Configurar DEBUG=True
    - Configurar base de datos SQLite para desarrollo
    - Configurar ALLOWED_HOSTS=['localhost', '127.0.0.1']
    - _Requirements: 7.1_
  
  - [x] 13.3 Configurar settings de producción


    - Crear settings/production.py heredando de base
    - Configurar DEBUG=False
    - Cargar SECRET_KEY desde variable de entorno
    - Configurar base de datos PostgreSQL desde DATABASE_URL
    - Configurar ALLOWED_HOSTS desde variable de entorno
    - Configurar STATIC_ROOT y MEDIA_ROOT
    - Configurar logging a archivo
    - Configurar variables para servicio de firma digital
    - _Requirements: 7.1, 5.2_

- [x] 14. Implementar rate limiting para vistas públicas





  - Instalar django-ratelimit
  - Aplicar decorador @ratelimit a CertificateQueryView (10 requests/minuto por IP)
  - Aplicar decorador @ratelimit a CertificateVerificationView (20 requests/minuto por IP)
  - Configurar mensaje de error cuando se excede el límite
  - Escribir tests para rate limiting
  - _Requirements: 3.1, 4.1_

- [x] 15. Implementar sistema de logging




  - Configurar LOGGING en settings con RotatingFileHandler
  - Crear logger 'certificates' para eventos generales
  - Crear logger 'certificates.signature' para firma digital
  - Agregar logging en ExcelProcessorService (info y errores)
  - Agregar logging en CertificateGeneratorService (info y errores)
  - Agregar logging en DigitalSignatureService (debug, info y errores)
  - Escribir tests que verifican que se generan logs
  - _Requirements: 8.1, 8.2, 8.3_

- [x] 16. Crear comandos de management



  - Crear comando load_default_template que carga plantilla por defecto
  - Crear comando generate_certificates --event-id que genera certificados para un evento
  - Crear comando sign_certificates --event-id que firma certificados de un evento
  - Crear comando create_superuser_if_not_exists para deployment
  - Escribir tests para cada comando
  - _Requirements: 2.1, 5.1, 6.1_

- [x] 17. Escribir tests de integración completos





  - Crear test de flujo completo: importar → generar → firmar → consultar → verificar
  - Crear test de importación con archivo Excel real
  - Crear test de generación de certificados con plantilla real
  - Crear test de consulta pública con múltiples certificados
  - Crear test de verificación con QR válido e inválido
  - Verificar que todos los tests pasen
  - _Requirements: Todos_

- [x] 18. Crear documentación





  - Crear README.md con instrucciones de instalación
  - Documentar formato del archivo Excel requerido
  - Documentar variables de entorno necesarias
  - Crear guía de usuario para administradores
  - Crear guía de configuración del servicio de firma digital
  - Documentar comandos de management disponibles
  - _Requirements: 1.1, 5.2, 7.1_

- [x] 19. Preparar para deployment





  - Crear requirements.txt con todas las dependencias
  - Crear archivo .env.example con variables de entorno de ejemplo
  - Crear script de deployment (deploy.sh)
  - Crear configuración de ejemplo para Nginx
  - Crear configuración de ejemplo para Systemd
  - Crear script de backup de base de datos
  - Documentar proceso de deployment en README
  - _Requirements: 7.1_
