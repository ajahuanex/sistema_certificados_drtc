# Design Document

## Overview

El Sistema de Certificados de Capacitaciones DRTC Puno es una aplicación web Django que gestiona el ciclo completo de certificados de capacitación: desde la importación de participantes hasta la generación, firma digital y verificación de certificados. El sistema utiliza una arquitectura modular basada en el patrón MVT (Model-View-Template) de Django, con componentes especializados para procesamiento de Excel, generación de PDFs, códigos QR, y integración con servicios externos de firma digital.

### Tecnologías Principales

- **Backend**: Django 4.2+ (Python 3.10+)
- **Base de Datos**: PostgreSQL 14+
- **Procesamiento Excel**: openpyxl
- **Generación PDF**: ReportLab o WeasyPrint
- **Códigos QR**: qrcode + Pillow
- **Firma Digital**: requests (cliente HTTP REST)
- **Frontend Admin**: Django Admin personalizado + Bootstrap 5
- **Frontend Público**: HTML5, CSS3, JavaScript vanilla

## Architecture

### Arquitectura General

El sistema sigue una arquitectura de tres capas:

1. **Capa de Presentación**: Vistas Django (admin y públicas)
2. **Capa de Lógica de Negocio**: Services y Managers
3. **Capa de Datos**: Models Django con PostgreSQL

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    Capa de Presentación                  │
├──────────────────┬──────────────────┬───────────────────┤
│  Django Admin    │  API Views       │  Public Views     │
│  (Gestión)       │  (REST)          │  (Consulta DNI)   │
└────────┬─────────┴────────┬─────────┴─────────┬─────────┘
         │                  │                   │
┌────────▼──────────────────▼───────────────────▼─────────┐
│              Capa de Lógica de Negocio                   │
├──────────────┬──────────────┬──────────────┬────────────┤
│ Excel        │ Certificate  │ QR Code      │ Digital    │
│ Processor    │ Generator    │ Generator    │ Signature  │
└──────┬───────┴──────┬───────┴──────┬───────┴─────┬──────┘
       │              │              │             │
┌──────▼──────────────▼──────────────▼─────────────▼──────┐
│                   Capa de Datos                          │
├──────────────┬──────────────┬──────────────┬────────────┤
│ Event        │ Participant  │ Certificate  │ AuditLog   │
│ Model        │ Model        │ Model        │ Model      │
└──────────────┴──────────────┴──────────────┴────────────┘
         │                                         │
         └─────────────────┬───────────────────────┘
                           │
                  ┌────────▼────────┐
                  │   PostgreSQL    │
                  └─────────────────┘
```

### Flujo de Datos Principal

1. **Importación**: Excel → ExcelProcessor → Participant/Event Models → DB
2. **Generación**: DB → CertificateGenerator → PDF + QR → FileStorage
3. **Consulta**: DNI Input → View → DB Query → Certificate List → Response
4. **Verificación**: QR Scan → URL → View → DB Query → Certificate Details
5. **Firma**: Certificate → DigitalSignatureService → External API → Signed PDF → DB Update

## Components and Interfaces

### 1. Models (Capa de Datos)

#### Event Model
```python
class Event(models.Model):
    name = CharField(max_length=500)
    event_date = DateField()
    description = TextField(blank=True)
    template = ForeignKey('CertificateTemplate')
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

#### Participant Model
```python
class Participant(models.Model):
    ATTENDEE_TYPES = [
        ('ASISTENTE', 'Asistente'),
        ('PONENTE', 'Ponente'),
        ('ORGANIZADOR', 'Organizador'),
    ]
    
    dni = CharField(max_length=8, db_index=True)
    full_name = CharField(max_length=300)
    event = ForeignKey('Event', on_delete=CASCADE)
    attendee_type = CharField(max_length=20, choices=ATTENDEE_TYPES)
    created_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['dni', 'event']]
        indexes = [Index(fields=['dni', 'event'])]
```

#### Certificate Model
```python
class Certificate(models.Model):
    uuid = UUIDField(default=uuid4, unique=True, editable=False)
    participant = OneToOneField('Participant', on_delete=CASCADE)
    pdf_file = FileField(upload_to='certificates/%Y/%m/')
    qr_code = ImageField(upload_to='qr_codes/%Y/%m/')
    generated_at = DateTimeField(auto_now_add=True)
    is_signed = BooleanField(default=False)
    signed_at = DateTimeField(null=True, blank=True)
    verification_url = URLField()
```

#### CertificateTemplate Model
```python
class CertificateTemplate(models.Model):
    name = CharField(max_length=200)
    html_template = TextField()
    css_styles = TextField(blank=True)
    background_image = ImageField(upload_to='templates/', blank=True)
    is_default = BooleanField(default=False)
    field_positions = JSONField()  # Coordenadas para campos
```

#### AuditLog Model
```python
class AuditLog(models.Model):
    ACTION_TYPES = [
        ('IMPORT', 'Importación Excel'),
        ('GENERATE', 'Generación Certificado'),
        ('SIGN', 'Firma Digital'),
        ('QUERY', 'Consulta DNI'),
        ('VERIFY', 'Verificación QR'),
    ]
    
    action_type = CharField(max_length=20, choices=ACTION_TYPES)
    user = ForeignKey(User, null=True, on_delete=SET_NULL)
    description = TextField()
    metadata = JSONField(default=dict)
    ip_address = GenericIPAddressField(null=True)
    timestamp = DateTimeField(auto_now_add=True)
```

### 2. Services (Capa de Lógica de Negocio)

#### ExcelProcessorService
```python
class ExcelProcessorService:
    """Procesa archivos Excel y crea participantes"""
    
    REQUIRED_COLUMNS = ['DNI', 'Nombres y Apellidos', 'Fecha del Evento', 
                        'Tipo de Asistente', 'Nombre del Evento']
    
    def validate_file(self, file) -> tuple[bool, list[str]]
    def process_excel(self, file, user) -> dict
    def _parse_row(self, row) -> dict
    def _validate_row(self, row_data) -> tuple[bool, str]
    def _create_or_update_participant(self, row_data) -> Participant
```

**Responsabilidades**:
- Validar estructura del archivo Excel
- Parsear filas y validar datos
- Crear/actualizar eventos y participantes
- Generar reporte de importación
- Registrar auditoría

#### CertificateGeneratorService
```python
class CertificateGeneratorService:
    """Genera certificados PDF con códigos QR"""
    
    def generate_certificate(self, participant) -> Certificate
    def generate_bulk_certificates(self, event) -> list[Certificate]
    def _render_template(self, participant, template) -> bytes
    def _generate_qr_code(self, verification_url) -> Image
    def _create_pdf(self, html_content, qr_image) -> bytes
```

**Responsabilidades**:
- Renderizar plantilla con datos del participante
- Generar código QR con URL de verificación
- Crear PDF usando ReportLab/WeasyPrint
- Guardar archivos en storage
- Crear registro de Certificate

#### QRCodeService
```python
class QRCodeService:
    """Genera códigos QR para verificación"""
    
    def generate_qr(self, certificate_uuid) -> Image
    def get_verification_url(self, certificate_uuid) -> str
```

**Responsabilidades**:
- Generar URL de verificación única
- Crear imagen QR con librería qrcode
- Configurar tamaño y formato del QR

#### DigitalSignatureService
```python
class DigitalSignatureService:
    """Integración con servicio externo de firma digital"""
    
    def sign_certificate(self, certificate) -> bool
    def sign_bulk_certificates(self, certificates) -> dict
    def _send_to_signature_service(self, pdf_bytes) -> bytes
    def _update_certificate_status(self, certificate, signed_pdf) -> None
```

**Responsabilidades**:
- Enviar PDF al servicio REST externo
- Manejar autenticación con el servicio
- Recibir PDF firmado
- Actualizar estado del certificado
- Manejar errores y reintentos

### 3. Views (Capa de Presentación)

#### Admin Views (Django Admin Personalizado)

- EventAdmin: CRUD de eventos con acción bulk "Generar Certificados"
- ParticipantAdmin: Visualización y búsqueda de participantes
- CertificateAdmin: Gestión de certificados con acciones "Firmar" y "Descargar"
- CertificateTemplateAdmin: Gestión de plantillas
- AuditLogAdmin: Visualización de logs (solo lectura)

#### Public Views
```python
class CertificateQueryView(TemplateView):
    """Vista pública para consultar certificados por DNI"""
    template_name = 'certificates/query.html'
    
    def get(self, request)
    def post(self, request)  # Búsqueda por DNI

class CertificateVerificationView(DetailView):
    """Vista pública para verificar certificado por UUID"""
    template_name = 'certificates/verify.html'
    
    def get_object(self)  # Busca por UUID en URL
```

#### API Views (para importación y firma)
```python
class ExcelImportView(LoginRequiredMixin, FormView):
    """Vista para importar archivo Excel"""
    
    def form_valid(self, form)

class CertificateSignView(LoginRequiredMixin, View):
    """Vista para enviar certificados a firma"""
    
    def post(self, request)
```

### 4. Forms

#### ExcelImportForm
```python
class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(
        validators=[FileExtensionValidator(['xlsx', 'xls'])]
    )
    
    def clean_excel_file(self)
```

#### DNIQueryForm
```python
class DNIQueryForm(forms.Form):
    dni = forms.CharField(
        max_length=8,
        validators=[RegexValidator(r'^\d{8}$')]
    )
```

## Data Models

### Diagrama de Relaciones

```
┌─────────────────┐
│  Event          │
│  - id           │
│  - name         │
│  - event_date   │
│  - template_id  │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────────┐
│  Participant        │
│  - id               │
│  - dni              │
│  - full_name        │
│  - event_id         │
│  - attendee_type    │
└────────┬────────────┘
         │ 1
         │
         │ 1
┌────────▼────────────┐
│  Certificate        │
│  - id               │
│  - uuid             │
│  - participant_id   │
│  - pdf_file         │
│  - qr_code          │
│  - is_signed        │
│  - signed_at        │
└─────────────────────┘

┌─────────────────────┐
│ CertificateTemplate │
│  - id               │
│  - name             │
│  - html_template    │
│  - is_default       │
└─────────────────────┘

┌─────────────────────┐
│  AuditLog           │
│  - id               │
│  - action_type      │
│  - user_id          │
│  - description      │
│  - timestamp        │
└─────────────────────┘
```

### Índices de Base de Datos

Para optimizar consultas frecuentes:

1. `Participant.dni` - Índice para búsquedas por DNI
2. `Participant(dni, event)` - Índice compuesto para unicidad
3. `Certificate.uuid` - Índice único para verificación
4. `Certificate.is_signed` - Índice para filtrar certificados firmados
5. `AuditLog.timestamp` - Índice para consultas por fecha
6. `AuditLog.action_type` - Índice para filtrar por tipo de acción

## Error Handling

### Estrategia de Manejo de Errores

#### 1. Errores de Importación Excel

**Tipos de Errores**:
- Archivo corrupto o formato inválido
- Columnas faltantes o mal nombradas
- Datos inválidos en filas (DNI, fecha, tipo)
- Errores de base de datos

**Manejo**:
```python
try:
    result = excel_processor.process_excel(file, user)
except InvalidFileFormat as e:
    messages.error(request, f"Archivo inválido: {e}")
except ValidationError as e:
    # Mostrar reporte de errores por fila
    return render(request, 'import_errors.html', {'errors': e.errors})
except Exception as e:
    logger.error(f"Error inesperado en importación: {e}")
    messages.error(request, "Error al procesar archivo")
```

**Reporte de Errores**:
- Archivo Excel con filas erróneas marcadas
- Descripción específica del error por fila
- Contador de éxitos vs errores

#### 2. Errores de Generación de Certificados

**Tipos de Errores**:
- Plantilla no encontrada o inválida
- Error al renderizar PDF
- Error al generar QR
- Falta de espacio en storage

**Manejo**:
```python
try:
    certificate = generator.generate_certificate(participant)
except TemplateNotFound:
    # Usar plantilla por defecto
    certificate = generator.generate_certificate(participant, use_default=True)
except PDFGenerationError as e:
    logger.error(f"Error generando PDF: {e}")
    raise
finally:
    # Registrar intento en auditoría
    AuditLog.objects.create(...)
```

#### 3. Errores de Firma Digital

**Tipos de Errores**:
- Servicio externo no disponible (timeout, 500)
- Autenticación fallida (401, 403)
- Certificado ya firmado
- Formato de respuesta inválido

**Manejo**:
```python
class DigitalSignatureService:
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # segundos
    
    def sign_certificate(self, certificate):
        for attempt in range(self.MAX_RETRIES):
            try:
                signed_pdf = self._send_to_signature_service(certificate.pdf_file)
                self._update_certificate_status(certificate, signed_pdf)
                return True
            except requests.Timeout:
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                    continue
                logger.error(f"Timeout firmando certificado {certificate.uuid}")
                return False
            except requests.HTTPError as e:
                logger.error(f"Error HTTP {e.response.status_code}: {e}")
                return False
```

**Estado de Firma**:
- Pendiente: Certificado generado pero no enviado
- En Proceso: Enviado al servicio externo
- Firmado: Completado exitosamente
- Error: Falló después de reintentos

#### 4. Errores de Consulta Pública

**Tipos de Errores**:
- DNI inválido
- Sin certificados encontrados
- Error de base de datos

**Manejo**:
```python
def post(self, request):
    form = DNIQueryForm(request.POST)
    if not form.is_valid():
        return render(request, 'query.html', {
            'form': form,
            'error': 'DNI inválido. Debe tener 8 dígitos.'
        })
    
    try:
        certificates = Certificate.objects.filter(
            participant__dni=form.cleaned_data['dni']
        ).select_related('participant__event')
        
        if not certificates.exists():
            return render(request, 'query.html', {
                'form': form,
                'message': 'No se encontraron certificados para este DNI.'
            })
        
        return render(request, 'results.html', {'certificates': certificates})
    except Exception as e:
        logger.error(f"Error en consulta: {e}")
        return render(request, 'query.html', {
            'form': form,
            'error': 'Error al buscar certificados. Intente nuevamente.'
        })
```

### Logging

**Configuración de Logs**:
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/certificates.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'certificates': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'certificates.signature': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    },
}
```

## Testing Strategy

### 1. Unit Tests

#### Models

```python
class ParticipantModelTest(TestCase):
    def test_unique_dni_per_event(self)
    def test_dni_validation(self)
    def test_attendee_type_choices(self)

class CertificateModelTest(TestCase):
    def test_uuid_generation(self)
    def test_verification_url_generation(self)
    def test_one_to_one_with_participant(self)
```

#### Services
```python
class ExcelProcessorServiceTest(TestCase):
    def test_validate_file_with_correct_columns(self)
    def test_validate_file_with_missing_columns(self)
    def test_process_valid_excel(self)
    def test_process_excel_with_invalid_dni(self)
    def test_process_excel_with_duplicate_dni(self)
    def test_create_or_update_participant(self)

class CertificateGeneratorServiceTest(TestCase):
    def test_generate_certificate_creates_pdf(self)
    def test_generate_certificate_creates_qr(self)
    def test_generate_bulk_certificates(self)
    def test_use_default_template_when_missing(self)

class DigitalSignatureServiceTest(TestCase):
    def test_sign_certificate_success(self)
    def test_sign_certificate_with_timeout(self)
    def test_sign_certificate_with_http_error(self)
    def test_retry_logic(self)
    def test_prevent_double_signing(self)
```

### 2. Integration Tests

```python
class CertificateWorkflowTest(TestCase):
    """Prueba el flujo completo: importar → generar → firmar"""
    
    def test_full_workflow(self):
        # 1. Importar Excel
        file = self._create_test_excel()
        result = ExcelProcessorService().process_excel(file, self.user)
        self.assertEqual(result['success_count'], 10)
        
        # 2. Generar certificados
        event = Event.objects.first()
        certificates = CertificateGeneratorService().generate_bulk_certificates(event)
        self.assertEqual(len(certificates), 10)
        
        # 3. Firmar certificados
        for cert in certificates:
            success = DigitalSignatureService().sign_certificate(cert)
            self.assertTrue(success)
            cert.refresh_from_db()
            self.assertTrue(cert.is_signed)

class PublicQueryTest(TestCase):
    """Prueba consulta pública por DNI"""
    
    def test_query_with_valid_dni(self)
    def test_query_with_invalid_dni(self)
    def test_query_with_no_results(self)
    def test_download_certificate_pdf(self)

class QRVerificationTest(TestCase):
    """Prueba verificación mediante QR"""
    
    def test_verify_valid_certificate(self)
    def test_verify_invalid_uuid(self)
    def test_verify_shows_signature_status(self)
```

### 3. End-to-End Tests

```python
class E2EAdminWorkflowTest(LiveServerTestCase):
    """Pruebas E2E con Selenium"""
    
    def test_admin_import_and_generate_workflow(self):
        # Login
        # Navegar a importación
        # Subir archivo
        # Verificar mensaje de éxito
        # Navegar a eventos
        # Generar certificados
        # Verificar creación

class E2EPublicQueryTest(LiveServerTestCase):
    def test_user_queries_and_downloads_certificate(self):
        # Navegar a página pública
        # Ingresar DNI
        # Verificar lista de certificados
        # Descargar PDF
```

### 4. Performance Tests

```python
class PerformanceTest(TestCase):
    def test_import_large_excel_file(self):
        """Importar 1000 participantes"""
        file = self._create_large_excel(1000)
        start = time.time()
        result = ExcelProcessorService().process_excel(file, self.user)
        duration = time.time() - start
        self.assertLess(duration, 30)  # Menos de 30 segundos
    
    def test_generate_bulk_certificates(self):
        """Generar 500 certificados"""
        participants = self._create_participants(500)
        start = time.time()
        certificates = CertificateGeneratorService().generate_bulk_certificates(event)
        duration = time.time() - start
        self.assertLess(duration, 60)  # Menos de 1 minuto
    
    def test_query_by_dni_performance(self):
        """Consulta con 10000 certificados en DB"""
        self._create_certificates(10000)
        start = time.time()
        certificates = Certificate.objects.filter(participant__dni='12345678')
        list(certificates)  # Forzar evaluación
        duration = time.time() - start
        self.assertLess(duration, 0.5)  # Menos de 500ms
```

### 5. Test Coverage

**Objetivo**: Mínimo 80% de cobertura de código

**Herramientas**:
- `coverage.py` para medir cobertura
- `pytest-cov` para integración con pytest

**Comando**:
```bash
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Security Considerations

### 1. Autenticación y Autorización

- Django Admin protegido con autenticación
- Permisos por modelo (add, change, delete, view)
- Vistas públicas sin autenticación (query, verify)
- CSRF protection en todos los formularios

### 2. Validación de Entrada

```python
# DNI: Solo 8 dígitos
dni_validator = RegexValidator(r'^\d{8}$', 'DNI debe tener 8 dígitos')

# Archivos Excel: Solo .xlsx, .xls
FileExtensionValidator(['xlsx', 'xls'])

# Tamaño máximo de archivo: 10MB
MAX_UPLOAD_SIZE = 10 * 1024 * 1024
```

### 3. Protección contra Inyección

- Uso de ORM Django (previene SQL injection)
- Escape automático en templates (previene XSS)
- Validación de datos antes de renderizar PDFs

### 4. Seguridad de Archivos

```python
# Storage seguro para PDFs y QRs
MEDIA_ROOT = '/var/www/certificates/media/'
MEDIA_URL = '/media/'

# Servir archivos con permisos controlados
def download_certificate(request, uuid):
    certificate = get_object_or_404(Certificate, uuid=uuid)
    # Verificar permisos si es necesario
    return FileResponse(certificate.pdf_file)
```

### 5. Comunicación con Servicio Externo

```python
# HTTPS obligatorio
SIGNATURE_SERVICE_URL = 'https://firma.gob.pe/api/sign'

# Autenticación con API Key
headers = {
    'Authorization': f'Bearer {settings.SIGNATURE_API_KEY}',
    'Content-Type': 'application/pdf'
}

# Timeout para prevenir bloqueos
response = requests.post(url, data=pdf_bytes, headers=headers, timeout=30)
```

### 6. Rate Limiting

```python
# Limitar consultas públicas por IP
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m', method='POST')
def certificate_query_view(request):
    # Máximo 10 consultas por minuto por IP
    pass
```

### 7. Auditoría de Seguridad

- Registrar todos los accesos administrativos
- Registrar consultas públicas con IP
- Alertas para intentos de acceso no autorizado
- Logs de errores de autenticación

## Configuration

### Settings Structure

```python
# settings/base.py - Configuración común
# settings/development.py - Desarrollo local
# settings/production.py - Producción

# Variables de entorno (.env)
SECRET_KEY=...
DEBUG=False
DATABASE_URL=postgresql://user:pass@localhost/dbname
SIGNATURE_API_KEY=...
SIGNATURE_SERVICE_URL=https://...
ALLOWED_HOSTS=certificados.drtcpuno.gob.pe
```

### Required Environment Variables

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=certificados.drtcpuno.gob.pe

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/certificates_db

# Media Storage
MEDIA_ROOT=/var/www/certificates/media/
MEDIA_URL=/media/

# Digital Signature Service
SIGNATURE_API_KEY=your-api-key-here
SIGNATURE_SERVICE_URL=https://firma.gob.pe/api/sign
SIGNATURE_TIMEOUT=30

# Email (para notificaciones)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=certificados@drtcpuno.gob.pe
EMAIL_HOST_PASSWORD=...
EMAIL_USE_TLS=True
```

### Dependencies (requirements.txt)

```
Django==4.2.7
psycopg2-binary==2.9.9
openpyxl==3.1.2
reportlab==4.0.7
weasyprint==60.1
qrcode[pil]==7.4.2
Pillow==10.1.0
requests==2.31.0
django-environ==0.11.2
django-ratelimit==4.1.0
gunicorn==21.2.0
whitenoise==6.6.0
```

## Deployment

### Production Checklist

1. **Base de Datos**
   - PostgreSQL 14+ instalado
   - Base de datos creada
   - Usuario con permisos configurado
   - Backups automáticos configurados

2. **Servidor Web**
   - Nginx como reverse proxy
   - Gunicorn como WSGI server
   - SSL/TLS configurado (Let's Encrypt)
   - Static files servidos por Nginx

3. **Aplicación**
   - Variables de entorno configuradas
   - Migraciones ejecutadas
   - Superusuario creado
   - Static files recolectados
   - Plantilla por defecto creada

4. **Monitoreo**
   - Logs configurados
   - Alertas de errores
   - Monitoreo de espacio en disco
   - Monitoreo de performance

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name certificados.drtcpuno.gob.pe;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name certificados.drtcpuno.gob.pe;
    
    ssl_certificate /etc/letsencrypt/live/certificados.drtcpuno.gob.pe/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/certificados.drtcpuno.gob.pe/privkey.pem;
    
    location /static/ {
        alias /var/www/certificates/static/;
    }
    
    location /media/ {
        alias /var/www/certificates/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Systemd Service

```ini
[Unit]
Description=Certificates DRTC Gunicorn
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/certificates
Environment="PATH=/var/www/certificates/venv/bin"
ExecStart=/var/www/certificates/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    certificates.wsgi:application

[Install]
WantedBy=multi-user.target
```
