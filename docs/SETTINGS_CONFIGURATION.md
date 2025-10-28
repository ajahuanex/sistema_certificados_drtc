# Settings Configuration

## Overview

El proyecto utiliza una estructura modular de settings con tres archivos principales:

- `config/settings/base.py` - Configuración común para todos los entornos
- `config/settings/development.py` - Configuración para desarrollo local
- `config/settings/production.py` - Configuración para producción

## Estructura de Settings

### Base Settings (base.py)

Configuración común que incluye:

- **INSTALLED_APPS**: Incluye la aplicación 'certificates' y apps de Django
- **MIDDLEWARE**: Middleware estándar de Django para seguridad, sesiones, CSRF, etc.
- **TEMPLATES**: Configurado con directorio de templates en la raíz del proyecto
- **STATIC_URL y MEDIA_URL**: Configurados para servir archivos estáticos y media
- **Internacionalización**: 
  - `LANGUAGE_CODE = 'es-pe'` (Español - Perú)
  - `TIME_ZONE = 'America/Lima'`
- **Digital Signature Service**: Variables de configuración para el servicio de firma digital

### Development Settings (development.py)

Configuración para desarrollo local:

- `DEBUG = True`
- `ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']`
- Base de datos SQLite para facilitar desarrollo en Windows
- Email backend de consola (imprime emails en la terminal)
- Logging simplificado a consola con nivel DEBUG

### Production Settings (production.py)

Configuración para producción:

- `DEBUG = False`
- `SECRET_KEY` cargado desde variable de entorno (requerido)
- `ALLOWED_HOSTS` cargado desde variable de entorno
- Base de datos PostgreSQL configurada desde variables de entorno
- Configuraciones de seguridad:
  - SSL redirect
  - Secure cookies
  - HSTS headers
  - XSS protection
- WhiteNoise para servir archivos estáticos
- Email SMTP configurado
- Logging avanzado con RotatingFileHandler:
  - `logs/django.log` - Logs generales (ERROR level)
  - `logs/certificates.log` - Logs de la aplicación certificates (INFO level)
  - `logs/signature.log` - Logs del servicio de firma digital (DEBUG level)
- Variables del servicio de firma digital

## Variables de Entorno

### Requeridas en Producción

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=certificados.drtcpuno.gob.pe

# Database
DB_NAME=certificados_drtc
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Digital Signature Service
SIGNATURE_SERVICE_URL=https://firma.gob.pe/api/sign
SIGNATURE_API_KEY=your-api-key-here
SIGNATURE_TIMEOUT=30

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=certificados@drtcpuno.gob.pe
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@drtcpuno.gob.pe
```

### Opcionales en Desarrollo

```bash
# Django
DJANGO_ENVIRONMENT=development
SECRET_KEY=django-insecure-key-for-dev
DEBUG=True

# Database (opcional, usa SQLite por defecto)
DB_NAME=certificados_drtc
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Digital Signature Service (opcional en desarrollo)
SIGNATURE_SERVICE_URL=
SIGNATURE_API_KEY=
SIGNATURE_TIMEOUT=30
```

## Uso

### Desarrollo

```bash
# Usar settings de desarrollo (por defecto)
python manage.py runserver

# O especificar explícitamente
python manage.py runserver --settings=config.settings.development
```

### Producción

```bash
# Configurar variable de entorno
export DJANGO_SETTINGS_MODULE=config.settings.production

# O especificar en el comando
python manage.py migrate --settings=config.settings.production
gunicorn config.wsgi:application --settings=config.settings.production
```

## Logging

### Desarrollo

Los logs se imprimen en la consola con formato simple:

```
INFO mensaje de log
DEBUG mensaje de debug
ERROR mensaje de error
```

### Producción

Los logs se escriben en archivos rotativos (10MB máximo, 5 backups):

- **django.log**: Errores generales de Django
- **certificates.log**: Logs de la aplicación (importaciones, generación de certificados)
- **signature.log**: Logs detallados del servicio de firma digital

## Servicio de Firma Digital

Las siguientes variables configuran la integración con el servicio externo de firma digital:

- `SIGNATURE_SERVICE_URL`: URL del endpoint REST del servicio de firma
- `SIGNATURE_API_KEY`: API key para autenticación con el servicio
- `SIGNATURE_TIMEOUT`: Timeout en segundos para las peticiones HTTP (default: 30)

Estas variables están disponibles en todos los entornos y pueden ser accedidas desde el código:

```python
from django.conf import settings

url = settings.SIGNATURE_SERVICE_URL
api_key = settings.SIGNATURE_API_KEY
timeout = settings.SIGNATURE_TIMEOUT
```

## Seguridad en Producción

El archivo `production.py` incluye las siguientes medidas de seguridad:

1. **HTTPS obligatorio**: `SECURE_SSL_REDIRECT = True`
2. **Cookies seguras**: `SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True`
3. **HSTS**: Headers de seguridad HTTP Strict Transport Security
4. **XSS Protection**: `SECURE_BROWSER_XSS_FILTER = True`
5. **Content Type Sniffing**: `SECURE_CONTENT_TYPE_NOSNIFF = True`
6. **Frame Options**: `X_FRAME_OPTIONS = 'DENY'`

## Notas

- El archivo `.env` no debe ser commiteado al repositorio
- Usar `.env.example` como plantilla para crear tu `.env` local
- En producción, las variables de entorno deben configurarse en el servidor (no usar archivo .env)
- Los logs en producción rotan automáticamente para evitar llenar el disco
