# Configuración del Servicio de Firma Digital

Esta guía proporciona instrucciones detalladas para configurar e integrar el servicio de firma digital con el Sistema de Certificados DRTC Puno.

## Tabla de Contenidos

- [Introducción](#introducción)
- [Requisitos Previos](#requisitos-previos)
- [Configuración Básica](#configuración-básica)
- [Especificaciones Técnicas](#especificaciones-técnicas)
- [Adaptación a Diferentes Servicios](#adaptación-a-diferentes-servicios)
- [Testing y Validación](#testing-y-validación)
- [Monitoreo y Logs](#monitoreo-y-logs)
- [Troubleshooting](#troubleshooting)
- [Servicio Mock para Desarrollo](#servicio-mock-para-desarrollo)

## Introducción

El Sistema de Certificados DRTC Puno incluye integración con servicios externos de firma digital para agregar validez legal a los certificados generados. Esta integración se realiza mediante una API REST que recibe archivos PDF y retorna los mismos archivos con firma digital aplicada.

### Flujo de Firma Digital

```
┌─────────────────┐
│   Certificado   │
│   PDF Generado  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Sistema DRTC Puno      │
│  (DigitalSignatureService)│
└────────┬────────────────┘
         │ HTTP POST
         │ (PDF binario)
         ▼
┌─────────────────────────┐
│  Servicio de Firma      │
│  Digital Externo        │
│  (API REST)             │
└────────┬────────────────┘
         │ HTTP 200
         │ (PDF firmado)
         ▼
┌─────────────────────────┐
│  Sistema DRTC Puno      │
│  (Actualiza certificado)│
└─────────────────────────┘
```

## Requisitos Previos

### 1. Acceso al Servicio de Firma Digital

Necesitas:

- ✅ URL del endpoint del servicio de firma
- ✅ Credenciales de autenticación (API Key, OAuth2, etc.)
- ✅ Documentación de la API del servicio
- ✅ Ambiente de pruebas (sandbox) para testing

### 2. Información Técnica Requerida

Antes de configurar, obtén la siguiente información del proveedor:

| Información | Ejemplo | Descripción |
|-------------|---------|-------------|
| URL del servicio | `https://firma.gob.pe/api/v1/sign` | Endpoint para firma de documentos |
| Método HTTP | `POST` | Método HTTP a utilizar |
| Tipo de autenticación | `Bearer Token` | Método de autenticación |
| API Key / Token | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | Credencial de acceso |
| Formato de entrada | `application/pdf` (binario) | Cómo enviar el PDF |
| Formato de salida | `application/pdf` (binario) | Cómo se recibe el PDF firmado |
| Timeout recomendado | `30 segundos` | Tiempo máximo de espera |
| Rate limits | `100 requests/minuto` | Límites de uso |

### 3. Requisitos de Red

- ✅ Conexión HTTPS (TLS 1.2 o superior)
- ✅ Acceso saliente al servicio (firewall configurado)
- ✅ Resolución DNS del dominio del servicio
- ✅ Certificados SSL válidos

## Configuración Básica

### 1. Variables de Entorno

Configura las siguientes variables en tu archivo `.env`:

```bash
# URL del servicio de firma digital
SIGNATURE_SERVICE_URL=https://firma.gob.pe/api/v1/sign

# API Key para autenticación
SIGNATURE_API_KEY=tu-api-key-aqui

# Timeout en segundos (opcional, default: 30)
SIGNATURE_TIMEOUT=30

# Número máximo de reintentos (opcional, default: 3)
SIGNATURE_MAX_RETRIES=3

# Delay entre reintentos en segundos (opcional, default: 5)
SIGNATURE_RETRY_DELAY=5
```

### 2. Configuración en Settings

El sistema carga automáticamente estas variables en `config/settings/production.py`:

```python
# Configuración del servicio de firma digital
SIGNATURE_SERVICE_URL = env('SIGNATURE_SERVICE_URL', default='')
SIGNATURE_API_KEY = env('SIGNATURE_API_KEY', default='')
SIGNATURE_TIMEOUT = env.int('SIGNATURE_TIMEOUT', default=30)
SIGNATURE_MAX_RETRIES = env.int('SIGNATURE_MAX_RETRIES', default=3)
SIGNATURE_RETRY_DELAY = env.int('SIGNATURE_RETRY_DELAY', default=5)
```

### 3. Verificar Configuración

Verifica que las variables estén configuradas correctamente:

```bash
python manage.py shell
```

```python
from django.conf import settings

print(f"URL: {settings.SIGNATURE_SERVICE_URL}")
print(f"API Key configurada: {'Sí' if settings.SIGNATURE_API_KEY else 'No'}")
print(f"Timeout: {settings.SIGNATURE_TIMEOUT}s")
print(f"Max Retries: {settings.SIGNATURE_MAX_RETRIES}")
```

## Especificaciones Técnicas

### Formato de Petición Estándar

El sistema envía peticiones HTTP POST con el siguiente formato:

#### Headers

```http
POST /api/v1/sign HTTP/1.1
Host: firma.gob.pe
Authorization: Bearer {SIGNATURE_API_KEY}
Content-Type: application/pdf
Content-Length: {tamaño_del_archivo}
```

#### Body

- Archivo PDF en formato binario (raw bytes)
- No se usa multipart/form-data
- No se usa base64 encoding

#### Ejemplo con cURL

```bash
curl -X POST https://firma.gob.pe/api/v1/sign \
  -H "Authorization: Bearer tu-api-key" \
  -H "Content-Type: application/pdf" \
  --data-binary @certificado.pdf \
  -o certificado_firmado.pdf
```

### Formato de Respuesta Esperada

#### Respuesta Exitosa

```http
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Length: {tamaño_del_archivo_firmado}

{PDF_firmado_en_binario}
```

#### Respuestas de Error

| Status Code | Significado | Acción del Sistema |
|-------------|-------------|-------------------|
| 400 Bad Request | Formato de petición inválido | Registra error, no reintenta |
| 401 Unauthorized | API Key inválida o expirada | Registra error, no reintenta |
| 403 Forbidden | Sin permisos | Registra error, no reintenta |
| 408 Request Timeout | Timeout del servidor | Reintenta hasta MAX_RETRIES |
| 429 Too Many Requests | Rate limit excedido | Espera y reintenta |
| 500 Internal Server Error | Error del servidor | Reintenta hasta MAX_RETRIES |
| 503 Service Unavailable | Servicio no disponible | Reintenta hasta MAX_RETRIES |

### Lógica de Reintentos

El sistema implementa reintentos automáticos con backoff exponencial:

```python
for attempt in range(MAX_RETRIES):
    try:
        response = requests.post(url, data=pdf_bytes, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        return response.content
    except (requests.Timeout, requests.HTTPError) as e:
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY * (attempt + 1))  # Backoff exponencial
            continue
        raise
```

## Adaptación a Diferentes Servicios

### Servicio con JSON y Base64

Si tu servicio requiere enviar el PDF en base64 dentro de un JSON:

#### 1. Modificar `certificates/services/digital_signature.py`

```python
import base64
import json

def _send_to_signature_service(self, pdf_bytes):
    """Envía PDF al servicio de firma (formato JSON con base64)"""
    
    # Convertir PDF a base64
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    
    # Preparar payload JSON
    payload = {
        'document': pdf_base64,
        'format': 'pdf',
        'signature_type': 'digital',
        'reason': 'Certificado de capacitación DRTC Puno',
        'location': 'Puno, Perú'
    }
    
    headers = {
        'Authorization': f'Bearer {self.api_key}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        self.service_url,
        json=payload,
        headers=headers,
        timeout=self.timeout
    )
    
    response.raise_for_status()
    
    # Extraer PDF firmado de la respuesta JSON
    response_data = response.json()
    signed_pdf_base64 = response_data['signed_document']
    signed_pdf_bytes = base64.b64decode(signed_pdf_base64)
    
    return signed_pdf_bytes
```

#### 2. Actualizar variables de entorno

```bash
# Agregar configuración adicional si es necesaria
SIGNATURE_REASON="Certificado de capacitación DRTC Puno"
SIGNATURE_LOCATION="Puno, Perú"
```

### Servicio con Multipart Form Data

Si tu servicio requiere multipart/form-data:

```python
def _send_to_signature_service(self, pdf_bytes):
    """Envía PDF al servicio de firma (formato multipart)"""
    
    headers = {
        'Authorization': f'Bearer {self.api_key}'
    }
    
    files = {
        'file': ('certificado.pdf', pdf_bytes, 'application/pdf')
    }
    
    data = {
        'signature_type': 'digital',
        'reason': 'Certificado de capacitación'
    }
    
    response = requests.post(
        self.service_url,
        files=files,
        data=data,
        headers=headers,
        timeout=self.timeout
    )
    
    response.raise_for_status()
    return response.content
```

### Servicio con OAuth2

Si tu servicio usa OAuth2 en lugar de API Key:

#### 1. Agregar método para obtener token

```python
def _get_access_token(self):
    """Obtiene token de acceso OAuth2"""
    token_url = settings.SIGNATURE_TOKEN_URL
    client_id = settings.SIGNATURE_CLIENT_ID
    client_secret = settings.SIGNATURE_CLIENT_SECRET
    
    response = requests.post(
        token_url,
        data={
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'signature:write'
        }
    )
    
    response.raise_for_status()
    token_data = response.json()
    
    # Cachear token (opcional)
    self._cached_token = token_data['access_token']
    self._token_expires_at = time.time() + token_data['expires_in']
    
    return token_data['access_token']

def _send_to_signature_service(self, pdf_bytes):
    """Envía PDF al servicio de firma (OAuth2)"""
    
    # Obtener token (usa cache si está disponible)
    if not hasattr(self, '_cached_token') or time.time() >= self._token_expires_at:
        access_token = self._get_access_token()
    else:
        access_token = self._cached_token
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/pdf'
    }
    
    response = requests.post(
        self.service_url,
        data=pdf_bytes,
        headers=headers,
        timeout=self.timeout
    )
    
    response.raise_for_status()
    return response.content
```

#### 2. Agregar variables de entorno

```bash
SIGNATURE_TOKEN_URL=https://firma.gob.pe/oauth/token
SIGNATURE_CLIENT_ID=tu-client-id
SIGNATURE_CLIENT_SECRET=tu-client-secret
```

### Servicio con Certificado Cliente (mTLS)

Si tu servicio requiere autenticación con certificado cliente:

```python
def _send_to_signature_service(self, pdf_bytes):
    """Envía PDF al servicio de firma (mTLS)"""
    
    cert_path = settings.SIGNATURE_CLIENT_CERT
    key_path = settings.SIGNATURE_CLIENT_KEY
    
    headers = {
        'Content-Type': 'application/pdf'
    }
    
    response = requests.post(
        self.service_url,
        data=pdf_bytes,
        headers=headers,
        cert=(cert_path, key_path),  # Certificado cliente
        verify=True,  # Verificar certificado del servidor
        timeout=self.timeout
    )
    
    response.raise_for_status()
    return response.content
```

Variables de entorno:

```bash
SIGNATURE_CLIENT_CERT=/path/to/client-cert.pem
SIGNATURE_CLIENT_KEY=/path/to/client-key.pem
```

## Testing y Validación

### 1. Test Manual con Shell

```bash
python manage.py shell
```

```python
from certificates.services.digital_signature import DigitalSignatureService
from certificates.models import Certificate

# Obtener un certificado de prueba
cert = Certificate.objects.filter(is_signed=False).first()

if cert:
    # Intentar firmarlo
    service = DigitalSignatureService()
    result = service.sign_certificate(cert)
    
    if result:
        print("✅ Certificado firmado exitosamente")
        cert.refresh_from_db()
        print(f"Estado: {'Firmado' if cert.is_signed else 'No firmado'}")
        print(f"Fecha de firma: {cert.signed_at}")
    else:
        print("❌ Error al firmar certificado")
else:
    print("No hay certificados disponibles para firmar")
```

### 2. Test con Comando de Management

```bash
# Firmar un certificado de prueba
python manage.py sign_certificates --event-id 1
```

### 3. Test de Conectividad

Verifica la conectividad con el servicio:

```bash
python manage.py shell
```

```python
import requests
from django.conf import settings

url = settings.SIGNATURE_SERVICE_URL
api_key = settings.SIGNATURE_API_KEY

# Test de conectividad básico
try:
    response = requests.get(
        url.replace('/sign', '/health'),  # Endpoint de health check
        headers={'Authorization': f'Bearer {api_key}'},
        timeout=5
    )
    print(f"Status: {response.status_code}")
    print(f"Servicio disponible: {'Sí' if response.status_code == 200 else 'No'}")
except requests.exceptions.RequestException as e:
    print(f"Error de conectividad: {e}")
```

### 4. Test con PDF de Prueba

```python
from certificates.services.digital_signature import DigitalSignatureService
import os

# Leer un PDF de prueba
with open('test_certificate.pdf', 'rb') as f:
    pdf_bytes = f.read()

# Intentar firmar
service = DigitalSignatureService()
try:
    signed_pdf = service._send_to_signature_service(pdf_bytes)
    
    # Guardar PDF firmado
    with open('test_certificate_signed.pdf', 'wb') as f:
        f.write(signed_pdf)
    
    print("✅ PDF firmado exitosamente")
    print(f"Tamaño original: {len(pdf_bytes)} bytes")
    print(f"Tamaño firmado: {len(signed_pdf)} bytes")
except Exception as e:
    print(f"❌ Error: {e}")
```

### 5. Test Unitario

Crear test en `certificates/tests/test_digital_signature.py`:

```python
from unittest.mock import patch, Mock
from django.test import TestCase
from certificates.services.digital_signature import DigitalSignatureService

class DigitalSignatureServiceTest(TestCase):
    
    @patch('requests.post')
    def test_sign_certificate_success(self, mock_post):
        """Test firma exitosa"""
        # Mock de respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'PDF_FIRMADO'
        mock_post.return_value = mock_response
        
        # Crear certificado de prueba
        cert = self._create_test_certificate()
        
        # Firmar
        service = DigitalSignatureService()
        result = service.sign_certificate(cert)
        
        # Verificar
        self.assertTrue(result)
        cert.refresh_from_db()
        self.assertTrue(cert.is_signed)
        self.assertIsNotNone(cert.signed_at)
```

## Monitoreo y Logs

### Configuración de Logging

El sistema registra todas las operaciones de firma en `logs/signature.log`:

```python
# En config/settings/base.py
LOGGING = {
    'loggers': {
        'certificates.signature': {
            'handlers': ['signature_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'handlers': {
        'signature_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/signature.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
}
```

### Ver Logs en Tiempo Real

```bash
# Windows
powershell Get-Content logs\signature.log -Wait -Tail 50

# Linux/Mac
tail -f logs/signature.log
```

### Formato de Logs

```
2024-10-28 10:15:23 [INFO] Iniciando firma de certificado UUID: 123e4567-e89b-12d3-a456-426614174000
2024-10-28 10:15:23 [DEBUG] Enviando petición a: https://firma.gob.pe/api/v1/sign
2024-10-28 10:15:25 [INFO] Certificado firmado exitosamente en 2.3 segundos
2024-10-28 10:15:25 [INFO] Tamaño original: 245678 bytes, Tamaño firmado: 248901 bytes
```

### Métricas a Monitorear

1. **Tasa de éxito**
   - Porcentaje de firmas exitosas vs fallidas
   - Meta: > 95%

2. **Tiempo de respuesta**
   - Tiempo promedio de firma
   - Meta: < 5 segundos

3. **Errores**
   - Tipos de errores más comunes
   - Frecuencia de errores

4. **Rate limiting**
   - Número de peticiones por minuto
   - Verificar que no se exceda el límite

### Script de Monitoreo

```bash
#!/bin/bash
# monitor_signature.sh

LOG_FILE="logs/signature.log"

echo "=== Estadísticas de Firma Digital ==="
echo ""

# Firmas exitosas hoy
SUCCESS_COUNT=$(grep "$(date +%Y-%m-%d)" $LOG_FILE | grep -c "firmado exitosamente")
echo "Firmas exitosas hoy: $SUCCESS_COUNT"

# Errores hoy
ERROR_COUNT=$(grep "$(date +%Y-%m-%d)" $LOG_FILE | grep -c "ERROR")
echo "Errores hoy: $ERROR_COUNT"

# Tasa de éxito
if [ $SUCCESS_COUNT -gt 0 ]; then
    TOTAL=$((SUCCESS_COUNT + ERROR_COUNT))
    SUCCESS_RATE=$((SUCCESS_COUNT * 100 / TOTAL))
    echo "Tasa de éxito: $SUCCESS_RATE%"
fi

# Últimos errores
echo ""
echo "=== Últimos 5 Errores ==="
grep "ERROR" $LOG_FILE | tail -5
```

## Troubleshooting

### Error: Connection Timeout

**Síntoma:**
```
requests.exceptions.Timeout: HTTPSConnectionPool(host='firma.gob.pe', port=443): 
Read timed out. (read timeout=30)
```

**Causas posibles:**
1. Servicio de firma lento o sobrecargado
2. Problemas de red
3. Timeout configurado muy bajo

**Soluciones:**
```bash
# Aumentar timeout
SIGNATURE_TIMEOUT=60

# Verificar conectividad
ping firma.gob.pe
curl -I https://firma.gob.pe

# Verificar desde el servidor
telnet firma.gob.pe 443
```

### Error: 401 Unauthorized

**Síntoma:**
```
requests.exceptions.HTTPError: 401 Client Error: Unauthorized
```

**Causas posibles:**
1. API Key inválida o expirada
2. API Key mal configurada
3. Formato de autenticación incorrecto

**Soluciones:**
```bash
# Verificar API Key
echo $SIGNATURE_API_KEY

# Verificar formato de autenticación
# Debe ser: Bearer {api_key}

# Regenerar API Key en el panel del proveedor
# Actualizar en .env
```

### Error: 400 Bad Request

**Síntoma:**
```
requests.exceptions.HTTPError: 400 Client Error: Bad Request
```

**Causas posibles:**
1. PDF corrupto o inválido
2. Formato de petición incorrecto
3. Headers faltantes o incorrectos

**Soluciones:**
```python
# Verificar que el PDF sea válido
from PyPDF2 import PdfReader

with open('certificado.pdf', 'rb') as f:
    reader = PdfReader(f)
    print(f"Páginas: {len(reader.pages)}")
    print(f"Válido: Sí")

# Verificar headers enviados
# Revisar logs de debug
```

### Error: 500 Internal Server Error

**Síntoma:**
```
requests.exceptions.HTTPError: 500 Server Error: Internal Server Error
```

**Causas posibles:**
1. Error en el servicio de firma
2. PDF con características no soportadas
3. Problema temporal del servicio

**Soluciones:**
1. Reintentar (el sistema lo hace automáticamente)
2. Verificar estado del servicio con el proveedor
3. Probar con un PDF más simple
4. Contactar soporte del proveedor

### Error: SSL Certificate Verification Failed

**Síntoma:**
```
requests.exceptions.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Causas posibles:**
1. Certificado SSL del servicio inválido o expirado
2. Certificados raíz no instalados en el sistema

**Soluciones:**
```bash
# Verificar certificado SSL
openssl s_client -connect firma.gob.pe:443

# Actualizar certificados del sistema
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ca-certificates

# CentOS/RHEL
sudo yum update ca-certificates

# Temporalmente deshabilitar verificación (NO RECOMENDADO en producción)
# En digital_signature.py:
response = requests.post(url, data=pdf_bytes, headers=headers, verify=False)
```

## Servicio Mock para Desarrollo

Para desarrollo y testing sin un servicio real, puedes usar un servicio mock.

### Opción 1: Mock en el Código

```python
# En config/settings/development.py
USE_MOCK_SIGNATURE_SERVICE = True
```

```python
# En certificates/services/digital_signature.py

def _send_to_signature_service(self, pdf_bytes):
    """Envía PDF al servicio de firma"""
    
    # Usar mock en desarrollo
    if settings.USE_MOCK_SIGNATURE_SERVICE:
        logger.info("🔧 Usando servicio de firma MOCK (desarrollo)")
        time.sleep(2)  # Simular delay
        
        # Agregar metadata al PDF (opcional)
        # En producción, el servicio real agrega la firma digital
        return pdf_bytes
    
    # Código real del servicio
    # ...
```

### Opción 2: Servidor Mock Local

Crear un servidor Flask simple para simular el servicio:

```python
# mock_signature_server.py
from flask import Flask, request, send_file
import time
import io

app = Flask(__name__)

@app.route('/api/v1/sign', methods=['POST'])
def sign_document():
    # Verificar autenticación
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return {'error': 'Unauthorized'}, 401
    
    # Leer PDF
    pdf_bytes = request.data
    
    # Simular procesamiento
    time.sleep(2)
    
    # Retornar el mismo PDF (en producción, estaría firmado)
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=False
    )

@app.route('/health', methods=['GET'])
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
```

Ejecutar:

```bash
pip install flask
python mock_signature_server.py
```

Configurar en `.env`:

```bash
SIGNATURE_SERVICE_URL=http://127.0.0.1:5000/api/v1/sign
SIGNATURE_API_KEY=mock-api-key-for-testing
```

## Checklist de Configuración

Usa este checklist para verificar que todo esté configurado correctamente:

- [ ] Variables de entorno configuradas en `.env`
- [ ] API Key válida obtenida del proveedor
- [ ] URL del servicio correcta
- [ ] Conectividad verificada (ping, curl)
- [ ] Test manual exitoso con un certificado
- [ ] Logs configurados y funcionando
- [ ] Monitoreo implementado
- [ ] Documentación del proveedor revisada
- [ ] Contacto de soporte del proveedor disponible
- [ ] Plan de contingencia definido

## Contacto y Soporte

### Soporte del Sistema DRTC

- **Email**: soporte@drtcpuno.gob.pe
- **Documentación**: Ver README.md principal

### Soporte del Proveedor de Firma Digital

Contacta directamente con tu proveedor de servicio de firma digital para:

- Problemas de autenticación
- Errores del servicio
- Cambios en la API
- Renovación de credenciales
- Consultas técnicas

---

**Última actualización:** 28 de octubre de 2024
