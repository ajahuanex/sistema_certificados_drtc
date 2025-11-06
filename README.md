# Sistema de Certificados DRTC Puno

Sistema de gestión y emisión de certificados digitales para eventos de capacitación de la Dirección Regional de Transportes y Comunicaciones de Puno.

## Características Principales

- ✅ Importación masiva de participantes desde archivos Excel
- ✅ Generación automática de certificados PDF personalizados
- ✅ Códigos QR únicos para verificación de autenticidad
- ✅ Integración con servicio externo de firma digital
- ✅ Consulta pública de certificados por DNI
- ✅ Verificación de certificados mediante escaneo de QR
- ✅ Panel de administración completo
- ✅ Sistema de auditoría y logging
- ✅ Rate limiting para protección de endpoints públicos

## Tabla de Contenidos

- [Requisitos del Sistema](#requisitos-del-sistema)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Formato del Archivo Excel](#formato-del-archivo-excel)
- [Comandos de Management](#comandos-de-management)
- [Guía de Usuario para Administradores](#guía-de-usuario-para-administradores)
- [Configuración del Servicio de Firma Digital](#configuración-del-servicio-de-firma-digital)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Requisitos del Sistema

### Software Requerido

- **Python**: 3.10 o superior
- **PostgreSQL**: 14 o superior (13+ también funciona)
- **pip**: Gestor de paquetes de Python
- **Git**: Para clonar el repositorio

### Dependencias Python Principales

- Django 4.2+
- psycopg2-binary (driver PostgreSQL)
- openpyxl (procesamiento de Excel)
- WeasyPrint (generación de PDFs)
- qrcode + Pillow (generación de códigos QR)
- requests (cliente HTTP para firma digital)
- django-ratelimit (protección contra abuso)

## 🚀 Instalación y Despliegue

### 🐳 **Despliegue con Docker (Recomendado para Producción)**

#### Opción A: Prueba Rápida Local
```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/sistema-certificados-drtc.git
cd sistema-certificados-drtc

# Ejecutar script de prueba automático
# Windows:
test-production-local.bat

# Linux/Mac:
chmod +x test-production-local.sh
./test-production-local.sh
```

#### Opción B: Despliegue Manual
```bash
# 1. Configurar variables de entorno
cp .env.production.example .env.production
# Editar .env.production con tus configuraciones

# 2. Construir y ejecutar
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 3. Verificar estado
docker-compose -f docker-compose.prod.yml ps
```

#### 🔧 **Troubleshooting Docker**
Si hay problemas, consulta: `COMANDOS_TROUBLESHOOTING.md`

### 💻 **Instalación Local (Desarrollo)**

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-organizacion/sistema-certificados-drtc.git
cd sistema-certificados-drtc
```

### 2. Crear Entorno Virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Nota para Windows:** Si tienes problemas instalando WeasyPrint, consulta la [documentación oficial](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows).

### 4. Configurar Variables de Entorno

Copia el archivo de ejemplo y edítalo con tus valores:

```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Edita el archivo `.env` con tus configuraciones (ver sección [Configuración](#configuración)).

### 5. Configurar Base de Datos

**Crear base de datos PostgreSQL:**

```sql
CREATE DATABASE certificados_drtc;
CREATE USER certificados_user WITH PASSWORD 'tu_password_seguro';
ALTER ROLE certificados_user SET client_encoding TO 'utf8';
ALTER ROLE certificados_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE certificados_user SET timezone TO 'America/Lima';
GRANT ALL PRIVILEGES ON DATABASE certificados_drtc TO certificados_user;
```

**Nota:** Para desarrollo local, puedes usar SQLite (configurado por defecto en `development.py`).

### 6. Ejecutar Migraciones

```bash
python manage.py migrate
```

### 7. Cargar Plantilla de Certificado por Defecto

```bash
python manage.py load_default_template
```

### 8. Crear Superusuario

```bash
python manage.py createsuperuser
```

Sigue las instrucciones para crear tu usuario administrador.

### 9. Iniciar Servidor de Desarrollo

```bash
python manage.py runserver
```

El sistema estará disponible en: `http://127.0.0.1:8000/`

**Panel de administración:** `http://127.0.0.1:8000/admin/`

### Inicio Rápido (Windows)

Alternativamente, puedes usar el script de inicio:

```bash
start.bat
```

Este script automáticamente:
- Activa el entorno virtual
- Verifica dependencias
- Aplica migraciones pendientes
- Inicia el servidor de desarrollo

## Estructura del Proyecto

```
.
├── config/                 # Configuración del proyecto Django
│   ├── settings/          # Settings modulares (base, development, production)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── certificates/          # Aplicación principal
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   └── ...
├── static/               # Archivos estáticos
├── media/                # Archivos subidos por usuarios
├── templates/            # Templates HTML
├── logs/                 # Logs de la aplicación
├── manage.py
└── requirements.txt
```

## Configuración de Entornos

El proyecto usa settings modulares:
- `base.py`: Configuración común
- `development.py`: Configuración de desarrollo
- `production.py`: Configuración de producción

Para cambiar el entorno, modifica la variable `DJANGO_ENVIRONMENT` en el archivo `.env`.

## Inicio Rápido (Windows)

Ejecuta el script de inicio:
```bash
start.bat
```

Este script:
- Activa el entorno virtual (si existe)
- Verifica las dependencias
- Aplica migraciones pendientes
- Inicia el servidor de desarrollo

## Comandos Útiles

```bash
# Ejecutar migraciones
python manage.py migrate

# Crear migraciones
python manage.py makemigrations

# Crear superusuario
python manage.py createsuperuser

# Recolectar archivos estáticos
python manage.py collectstatic

# Ejecutar tests
python manage.py test

# Ejecutar servidor de desarrollo
python manage.py runserver

# Verificar configuración
python manage.py check

# Verificar configuración de producción
python manage.py check --deploy
```

## Documentación Adicional

- [Configuración de PostgreSQL](docs/POSTGRESQL_SETUP.md)
- [Estructura del Proyecto](docs/PROJECT_STRUCTURE.md)

## Notas Importantes

### Base de Datos en Desarrollo

Por defecto, el proyecto usa SQLite en desarrollo para facilitar la configuración inicial en Windows. Para usar PostgreSQL:

1. Instala PostgreSQL y psycopg2 (ver `docs/POSTGRESQL_SETUP.md`)
2. Edita `config/settings/development.py`
3. Descomenta la configuración de PostgreSQL
4. Comenta la configuración de SQLite
5. Actualiza las credenciales en `.env`

### Entornos

El proyecto soporta múltiples entornos:
- **development**: Para desarrollo local (por defecto)
- **production**: Para producción

Cambia el entorno modificando `DJANGO_ENVIRONMENT` en `.env`.

## Configuración

### Variables de Entorno Requeridas

El archivo `.env` debe contener las siguientes variables:

#### Configuración de Django

```bash
# Entorno de ejecución (development o production)
DJANGO_ENVIRONMENT=development

# Clave secreta de Django (generar una nueva para producción)
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria

# Modo debug (True solo en desarrollo)
DEBUG=True

# Hosts permitidos (separados por coma)
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### Configuración de Base de Datos

```bash
# URL de conexión a PostgreSQL
# Formato: postgresql://usuario:password@host:puerto/nombre_db
DATABASE_URL=postgresql://certificados_user:tu_password@localhost:5432/certificados_drtc

# Para desarrollo con SQLite (alternativa)
# DATABASE_URL=sqlite:///db.sqlite3
```

#### Configuración de Archivos Media

```bash
# Ruta donde se guardarán los certificados PDF y códigos QR
MEDIA_ROOT=media/
MEDIA_URL=/media/
```

#### Configuración del Servicio de Firma Digital

```bash
# URL del servicio REST de firma digital
SIGNATURE_SERVICE_URL=https://firma.gob.pe/api/v1/sign

# API Key para autenticación con el servicio
SIGNATURE_API_KEY=tu-api-key-del-servicio-de-firma

# Timeout en segundos para las peticiones al servicio
SIGNATURE_TIMEOUT=30

# Número máximo de reintentos en caso de fallo
SIGNATURE_MAX_RETRIES=3

# Delay en segundos entre reintentos
SIGNATURE_RETRY_DELAY=5
```

#### Configuración de Email (Opcional)

```bash
# Para notificaciones por correo
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=certificados@drtcpuno.gob.pe
EMAIL_HOST_PASSWORD=tu-password-de-email
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=certificados@drtcpuno.gob.pe
```

#### Configuración de Logging

```bash
# Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Ruta del archivo de logs
LOG_FILE=logs/certificates.log
```

### Ejemplo Completo de .env

Ver el archivo `.env.example` incluido en el proyecto para un ejemplo completo con todos los valores.

## Formato del Archivo Excel

### Estructura Requerida

El archivo Excel para importar participantes **debe** contener las siguientes columnas (nombres exactos):

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| **DNI** | Texto/Número | Documento Nacional de Identidad (8 dígitos) | 12345678 |
| **Nombres y Apellidos** | Texto | Nombre completo del participante | Juan Pérez García |
| **Fecha del Evento** | Fecha | Fecha en que se realizó el evento | 15/10/2024 |
| **Tipo de Asistente** | Texto | Rol del participante | ASISTENTE |
| **Nombre del Evento** | Texto | Nombre completo del evento | Capacitación en Seguridad Vial |

### Valores Permitidos

#### Tipo de Asistente

Solo se aceptan los siguientes valores (sensible a mayúsculas):

- `ASISTENTE` - Participante regular del evento
- `PONENTE` - Expositor o presentador
- `ORGANIZADOR` - Organizador del evento

### Formato de Fecha

Las fechas pueden estar en cualquiera de estos formatos:

- `DD/MM/YYYY` (ejemplo: 15/10/2024)
- `DD-MM-YYYY` (ejemplo: 15-10-2024)
- `YYYY-MM-DD` (ejemplo: 2024-10-15)

### Validaciones

El sistema validará automáticamente:

1. ✅ **DNI**: Debe tener exactamente 8 dígitos numéricos
2. ✅ **Nombres y Apellidos**: No puede estar vacío
3. ✅ **Fecha del Evento**: Debe ser una fecha válida
4. ✅ **Tipo de Asistente**: Debe ser uno de los valores permitidos
5. ✅ **Nombre del Evento**: No puede estar vacío

### Ejemplo de Archivo Excel

```
| DNI      | Nombres y Apellidos    | Fecha del Evento | Tipo de Asistente | Nombre del Evento                |
|----------|------------------------|------------------|-------------------|----------------------------------|
| 12345678 | Juan Pérez García      | 15/10/2024       | ASISTENTE         | Capacitación en Seguridad Vial   |
| 87654321 | María López Quispe     | 15/10/2024       | PONENTE           | Capacitación en Seguridad Vial   |
| 11223344 | Carlos Mamani Flores   | 15/10/2024       | ORGANIZADOR       | Capacitación en Seguridad Vial   |
| 44332211 | Ana Torres Condori     | 15/10/2024       | ASISTENTE         | Capacitación en Seguridad Vial   |
```

### Manejo de Duplicados

- Si un participante con el mismo DNI ya existe para el mismo evento, se **actualizará** su información
- Si es un evento diferente, se creará un nuevo registro de participante

### Reporte de Errores

Después de la importación, el sistema mostrará:

- ✅ Número de registros importados exitosamente
- ❌ Número de registros con errores
- 📋 Detalle de errores por fila (número de fila y descripción del error)

### Descarga de Plantilla

Puedes descargar una plantilla de ejemplo desde el panel de administración en la sección de importación.

## Comandos de Management

El sistema incluye comandos personalizados de Django para facilitar tareas administrativas.

### load_default_template

Carga la plantilla de certificado por defecto en la base de datos.

```bash
python manage.py load_default_template
```

**Uso:**
- Ejecutar después de las migraciones iniciales
- Ejecutar si se elimina accidentalmente la plantilla por defecto
- Ejecutar después de actualizar el diseño de la plantilla

**Opciones:**
- `--force`: Sobrescribe la plantilla por defecto existente

```bash
python manage.py load_default_template --force
```

### generate_certificates

Genera certificados PDF para todos los participantes de un evento específico.

```bash
python manage.py generate_certificates --event-id <ID>
```

**Parámetros:**
- `--event-id <ID>`: ID del evento (requerido)

**Opciones:**
- `--regenerate`: Regenera certificados existentes

**Ejemplos:**

```bash
# Generar certificados para el evento con ID 1
python manage.py generate_certificates --event-id 1

# Regenerar todos los certificados del evento 1
python manage.py generate_certificates --event-id 1 --regenerate
```

**Salida:**
- Muestra progreso de generación
- Reporta número de certificados generados exitosamente
- Reporta errores si los hay

### sign_certificates

Envía certificados al servicio de firma digital.

```bash
python manage.py sign_certificates --event-id <ID>
```

**Parámetros:**
- `--event-id <ID>`: ID del evento (requerido)

**Opciones:**
- `--all`: Firma todos los certificados pendientes (ignora --event-id)
- `--retry-failed`: Reintenta firmar certificados que fallaron anteriormente

**Ejemplos:**

```bash
# Firmar certificados del evento 1
python manage.py sign_certificates --event-id 1

# Firmar todos los certificados pendientes
python manage.py sign_certificates --all

# Reintentar certificados que fallaron
python manage.py sign_certificates --event-id 1 --retry-failed
```

**Notas:**
- Solo firma certificados que no han sido firmados previamente
- Requiere configuración correcta del servicio de firma digital
- Muestra progreso y resultado de cada certificado

### create_superuser_if_not_exists

Crea un superusuario automáticamente si no existe ninguno (útil para deployment).

```bash
python manage.py create_superuser_if_not_exists
```

**Variables de entorno requeridas:**

```bash
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@drtcpuno.gob.pe
DJANGO_SUPERUSER_PASSWORD=password_seguro
```

**Uso:**
- En scripts de deployment automatizado
- En contenedores Docker
- En CI/CD pipelines

**Ejemplo en script de deployment:**

```bash
#!/bin/bash
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_EMAIL=admin@drtcpuno.gob.pe
export DJANGO_SUPERUSER_PASSWORD=$(openssl rand -base64 32)

python manage.py migrate
python manage.py create_superuser_if_not_exists
python manage.py load_default_template
```

### Comandos Django Estándar Útiles

```bash
# Ejecutar migraciones
python manage.py migrate

# Crear nuevas migraciones
python manage.py makemigrations

# Recolectar archivos estáticos (producción)
python manage.py collectstatic --noinput

# Ejecutar tests
python manage.py test

# Ejecutar tests con cobertura
coverage run --source='.' manage.py test
coverage report

# Verificar configuración
python manage.py check

# Verificar configuración de producción
python manage.py check --deploy

# Abrir shell de Django
python manage.py shell

# Abrir shell de base de datos
python manage.py dbshell
```

## Guía de Usuario para Administradores

### Acceso al Panel de Administración

1. Navega a: `http://tu-dominio.com/admin/`
2. Ingresa con tu usuario y contraseña de administrador
3. Verás el panel principal con las secciones disponibles

### 1. Gestión de Eventos

#### Crear un Evento

1. En el panel de administración, haz clic en **"Events"**
2. Haz clic en **"Add Event"** (Agregar Evento)
3. Completa los campos:
   - **Name**: Nombre del evento (ej: "Capacitación en Seguridad Vial 2024")
   - **Event date**: Fecha del evento
   - **Description**: Descripción opcional del evento
   - **Template**: Selecciona la plantilla de certificado (usa la por defecto si no tienes otra)
4. Haz clic en **"Save"**

#### Listar y Buscar Eventos

- En la lista de eventos puedes:
  - Buscar por nombre
  - Filtrar por fecha
  - Ordenar por columnas
  - Ver número de participantes

#### Generar Certificados para un Evento

1. En la lista de eventos, selecciona el evento
2. En el menú desplegable de acciones, selecciona **"Generar Certificados"**
3. Haz clic en **"Go"**
4. El sistema generará certificados para todos los participantes
5. Verás un mensaje de confirmación con el número de certificados generados

### 2. Importación de Participantes

#### Importar desde Excel

1. En el panel de administración, haz clic en **"Import Excel"** (Importar Excel)
2. Haz clic en **"Choose File"** y selecciona tu archivo Excel
3. Verifica que el archivo cumpla con el [formato requerido](#formato-del-archivo-excel)
4. Haz clic en **"Import"** (Importar)
5. El sistema procesará el archivo y mostrará:
   - ✅ Registros importados exitosamente
   - ❌ Errores encontrados (si los hay)
   - 📋 Detalle de cada error

#### Solución de Errores de Importación

Si hay errores:

1. Revisa el reporte de errores mostrado
2. Corrige los datos en el archivo Excel
3. Vuelve a importar el archivo

Errores comunes:
- DNI con formato incorrecto (debe tener 8 dígitos)
- Tipo de Asistente inválido (debe ser ASISTENTE, PONENTE u ORGANIZADOR)
- Fechas en formato incorrecto
- Columnas faltantes o mal nombradas

### 3. Gestión de Participantes

#### Ver Participantes

1. Haz clic en **"Participants"** en el panel de administración
2. Verás la lista de todos los participantes registrados

#### Buscar Participantes

Puedes buscar por:
- DNI
- Nombre completo
- Nombre del evento

#### Editar un Participante

1. Haz clic en el participante que deseas editar
2. Modifica los campos necesarios
3. Haz clic en **"Save"**

**Nota:** Si modificas datos de un participante que ya tiene certificado generado, deberás regenerar el certificado.

### 4. Gestión de Certificados

#### Ver Certificados

1. Haz clic en **"Certificates"** en el panel de administración
2. Verás la lista de certificados generados

#### Filtrar Certificados

Puedes filtrar por:
- Estado de firma (firmados / no firmados)
- Evento
- Fecha de generación

#### Descargar un Certificado

1. En la lista de certificados, haz clic en el certificado
2. En la página de detalles, haz clic en el enlace del archivo PDF
3. El certificado se descargará

#### Firmar Certificados

**Opción 1: Firmar certificados de un evento**

1. Ve a la lista de certificados
2. Filtra por el evento deseado
3. Selecciona los certificados a firmar (checkbox)
4. En el menú de acciones, selecciona **"Firmar Certificados"**
5. Haz clic en **"Go"**
6. El sistema enviará los certificados al servicio de firma digital
7. Verás un mensaje con el resultado

**Opción 2: Usar comando de management**

```bash
python manage.py sign_certificates --event-id 1
```

#### Regenerar un Certificado

Si necesitas regenerar un certificado (por ejemplo, después de editar datos del participante):

1. Elimina el certificado existente
2. Ve al evento correspondiente
3. Usa la acción **"Generar Certificados"**

### 5. Gestión de Plantillas

#### Ver Plantillas

1. Haz clic en **"Certificate Templates"** en el panel de administración
2. Verás las plantillas disponibles

#### Crear una Nueva Plantilla

1. Haz clic en **"Add Certificate Template"**
2. Completa los campos:
   - **Name**: Nombre descriptivo de la plantilla
   - **HTML Template**: Código HTML de la plantilla
   - **CSS Styles**: Estilos CSS personalizados
   - **Background Image**: Imagen de fondo (opcional)
   - **Is Default**: Marca si será la plantilla por defecto
   - **Field Positions**: JSON con posiciones de campos (avanzado)
3. Haz clic en **"Save"**

**Nota:** La creación de plantillas requiere conocimientos de HTML/CSS. Consulta con el equipo técnico.

### 6. Auditoría y Logs

#### Ver Registro de Auditoría

1. Haz clic en **"Audit Logs"** en el panel de administración
2. Verás todas las acciones registradas en el sistema

#### Filtrar Logs

Puedes filtrar por:
- Tipo de acción (importación, generación, firma, consulta, verificación)
- Usuario que realizó la acción
- Fecha

#### Información Registrada

Cada log incluye:
- Tipo de acción
- Usuario que la realizó
- Descripción detallada
- Metadata adicional (JSON)
- Dirección IP (para acciones públicas)
- Fecha y hora

### 7. Mejores Prácticas

#### Flujo de Trabajo Recomendado

1. **Crear el evento** en el sistema
2. **Importar participantes** desde Excel
3. **Verificar** que todos los participantes se importaron correctamente
4. **Generar certificados** para el evento
5. **Revisar** algunos certificados generados
6. **Firmar certificados** digitalmente
7. **Notificar** a los participantes que pueden consultar sus certificados

#### Respaldo de Datos

- Realiza respaldos regulares de la base de datos
- Mantén copias de los archivos Excel originales
- Respalda la carpeta `media/` con los certificados generados

#### Seguridad

- Cambia la contraseña del administrador regularmente
- No compartas las credenciales de administrador
- Revisa periódicamente el registro de auditoría
- Mantén actualizado el sistema

## Configuración del Servicio de Firma Digital

### Requisitos Previos

Para utilizar la funcionalidad de firma digital, necesitas:

1. **Acceso a un servicio de firma digital** compatible con REST API
2. **API Key** o credenciales de autenticación
3. **URL del endpoint** del servicio

### Configuración en el Sistema

#### 1. Variables de Entorno

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

#### 2. Formato de la Petición

El sistema envía peticiones HTTP POST al servicio de firma con:

**Headers:**
```
Authorization: Bearer {SIGNATURE_API_KEY}
Content-Type: application/pdf
```

**Body:**
- Archivo PDF en formato binario

**Ejemplo de petición:**

```python
import requests

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/pdf'
}

with open('certificado.pdf', 'rb') as pdf_file:
    response = requests.post(
        'https://firma.gob.pe/api/v1/sign',
        data=pdf_file.read(),
        headers=headers,
        timeout=30
    )
```

#### 3. Formato de la Respuesta Esperada

El servicio debe responder con:

**Status Code:** `200 OK`

**Body:** PDF firmado en formato binario

**Headers esperados:**
```
Content-Type: application/pdf
Content-Length: <tamaño del archivo>
```

### Adaptación a Diferentes Servicios

Si tu servicio de firma digital usa un formato diferente, necesitarás modificar el archivo `certificates/services/digital_signature.py`.

#### Ejemplo: Servicio con JSON

Si el servicio requiere enviar el PDF en base64 dentro de un JSON:

```python
# En digital_signature.py, método _send_to_signature_service

import base64
import json

def _send_to_signature_service(self, pdf_bytes):
    # Convertir PDF a base64
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    
    # Preparar payload JSON
    payload = {
        'document': pdf_base64,
        'format': 'pdf',
        'signature_type': 'digital'
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

#### Ejemplo: Servicio con Autenticación OAuth2

Si el servicio usa OAuth2:

```python
# Agregar método para obtener token

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
            'client_secret': client_secret
        }
    )
    
    response.raise_for_status()
    return response.json()['access_token']

def _send_to_signature_service(self, pdf_bytes):
    # Obtener token
    access_token = self._get_access_token()
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/pdf'
    }
    
    # ... resto del código
```

### Testing del Servicio de Firma

#### 1. Test Manual

Puedes probar la conexión con el servicio usando el shell de Django:

```python
python manage.py shell

from certificates.services.digital_signature import DigitalSignatureService
from certificates.models import Certificate

# Obtener un certificado de prueba
cert = Certificate.objects.first()

# Intentar firmarlo
service = DigitalSignatureService()
result = service.sign_certificate(cert)

print(f"Resultado: {result}")
```

#### 2. Test con Comando

```bash
# Firmar un certificado específico del evento 1
python manage.py sign_certificates --event-id 1
```

#### 3. Verificar Logs

Revisa los logs para ver detalles de la comunicación:

```bash
# Windows
type logs\signature.log

# Linux/Mac
tail -f logs/signature.log
```

### Troubleshooting del Servicio de Firma

#### Error: Connection Timeout

**Causa:** El servicio no responde en el tiempo configurado

**Solución:**
1. Verifica que la URL del servicio sea correcta
2. Aumenta el valor de `SIGNATURE_TIMEOUT`
3. Verifica tu conexión a internet
4. Contacta al proveedor del servicio

#### Error: 401 Unauthorized

**Causa:** API Key inválida o expirada

**Solución:**
1. Verifica que `SIGNATURE_API_KEY` sea correcta
2. Verifica que la API Key no haya expirado
3. Regenera la API Key en el panel del proveedor

#### Error: 400 Bad Request

**Causa:** Formato de petición incorrecto

**Solución:**
1. Verifica que el PDF sea válido
2. Revisa que el formato de la petición coincida con lo esperado por el servicio
3. Consulta la documentación del servicio de firma

#### Error: 500 Internal Server Error

**Causa:** Error en el servicio de firma

**Solución:**
1. Reintenta la operación (el sistema lo hace automáticamente)
2. Contacta al soporte del servicio de firma
3. Verifica el estado del servicio

### Servicio de Firma Mock (Desarrollo)

Para desarrollo y testing sin un servicio real, puedes usar un mock:

```python
# En config/settings/development.py

# Usar servicio mock en desarrollo
USE_MOCK_SIGNATURE_SERVICE = True
```

Luego modifica `digital_signature.py`:

```python
def _send_to_signature_service(self, pdf_bytes):
    if settings.USE_MOCK_SIGNATURE_SERVICE:
        # Simular firma (solo agrega metadata)
        logger.info("Usando servicio de firma MOCK")
        time.sleep(2)  # Simular delay
        return pdf_bytes  # Retornar el mismo PDF
    
    # Código real del servicio
    # ...
```


## Deployment

### Requisitos del Servidor

#### Hardware Mínimo Recomendado

- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disco**: 20 GB (más espacio según volumen de certificados)
- **Sistema Operativo**: Ubuntu 20.04 LTS o superior / Debian 11+

#### Software Requerido

- Python 3.10+
- PostgreSQL 14+
- Nginx
- Systemd
- Git

### Proceso de Deployment

#### 1. Preparación del Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install -y python3.10 python3.10-venv python3-pip postgresql postgresql-contrib nginx git

# Instalar dependencias para WeasyPrint
sudo apt install -y python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
```

#### 2. Configurar PostgreSQL

```bash
# Acceder a PostgreSQL
sudo -u postgres psql

# Crear base de datos y usuario
CREATE DATABASE certificados_drtc;
CREATE USER certificados_user WITH PASSWORD 'tu_password_seguro';
ALTER ROLE certificados_user SET client_encoding TO 'utf8';
ALTER ROLE certificados_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE certificados_user SET timezone TO 'America/Lima';
GRANT ALL PRIVILEGES ON DATABASE certificados_drtc TO certificados_user;
\q
```

#### 3. Clonar y Configurar el Proyecto

```bash
# Crear directorio del proyecto
sudo mkdir -p /var/www/certificates
sudo chown $USER:$USER /var/www/certificates

# Clonar repositorio
cd /var/www/certificates
git clone https://github.com/your-org/certificates-drtc.git .

# Crear entorno virtual
python3.10 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus valores
nano .env
```

Configuración mínima para producción:

```bash
DJANGO_ENVIRONMENT=production
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=certificados.drtcpuno.gob.pe

DATABASE_URL=postgresql://certificados_user:tu_password@localhost:5432/certificados_drtc

SIGNATURE_SERVICE_URL=https://firma.gob.pe/api/sign
SIGNATURE_API_KEY=tu-api-key-aqui
```

#### 5. Preparar la Aplicación

```bash
# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Cargar plantilla por defecto
python manage.py load_default_template

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Crear directorios necesarios
mkdir -p logs media/certificates media/qr_codes backups
```

#### 6. Configurar Gunicorn (Systemd)

```bash
# Copiar archivo de servicio
sudo cp certificates-drtc.service /etc/systemd/system/

# Editar si es necesario
sudo nano /etc/systemd/system/certificates-drtc.service

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicio
sudo systemctl enable certificates-drtc

# Iniciar servicio
sudo systemctl start certificates-drtc

# Verificar estado
sudo systemctl status certificates-drtc
```

#### 7. Configurar Nginx

```bash
# Copiar configuración
sudo cp nginx.conf.example /etc/nginx/sites-available/certificates-drtc

# Editar con tu dominio
sudo nano /etc/nginx/sites-available/certificates-drtc

# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/certificates-drtc /etc/nginx/sites-enabled/

# Probar configuración
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx
```

#### 8. Configurar SSL con Let's Encrypt

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d certificados.drtcpuno.gob.pe

# Verificar renovación automática
sudo certbot renew --dry-run
```

#### 9. Configurar Permisos

```bash
# Cambiar propietario
sudo chown -R www-data:www-data /var/www/certificates

# Configurar permisos
sudo chmod -R 755 /var/www/certificates
sudo chmod -R 775 /var/www/certificates/media
sudo chmod -R 775 /var/www/certificates/logs
```

#### 10. Configurar Backups Automáticos

```bash
# Hacer ejecutable el script de backup
chmod +x backup_database.sh

# Agregar a crontab para backups diarios a las 2 AM
crontab -e

# Agregar esta línea:
0 2 * * * /var/www/certificates/backup_database.sh >> /var/log/backup-certificates.log 2>&1
```

### Deployment Automatizado

Para deployment automatizado, usa el script incluido:

```bash
# Hacer ejecutable
chmod +x deploy.sh

# Ejecutar deployment
sudo ./deploy.sh
```

El script automáticamente:
- Actualiza el código desde Git
- Instala dependencias
- Ejecuta migraciones
- Recolecta archivos estáticos
- Reinicia servicios
- Verifica el estado

### Actualización de la Aplicación

Para actualizar a una nueva versión:

```bash
# Opción 1: Usar script de deployment
sudo ./deploy.sh

# Opción 2: Manual
cd /var/www/certificates
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart certificates-drtc
```

### Monitoreo y Logs

#### Ver Logs de la Aplicación

```bash
# Logs de Gunicorn
tail -f /var/www/certificates/logs/gunicorn-error.log
tail -f /var/www/certificates/logs/gunicorn-access.log

# Logs de la aplicación
tail -f /var/www/certificates/logs/certificates.log
tail -f /var/www/certificates/logs/signature.log

# Logs de Systemd
sudo journalctl -u certificates-drtc -f

# Logs de Nginx
sudo tail -f /var/log/nginx/certificates-drtc-error.log
sudo tail -f /var/log/nginx/certificates-drtc-access.log
```

#### Verificar Estado de Servicios

```bash
# Estado del servicio Django
sudo systemctl status certificates-drtc

# Estado de Nginx
sudo systemctl status nginx

# Estado de PostgreSQL
sudo systemctl status postgresql
```

### Backup y Restauración

#### Crear Backup Manual

```bash
# Backup completo (base de datos + archivos)
./backup_database.sh

# Solo base de datos
./backup_database.sh
```

#### Restaurar desde Backup

```bash
# Listar backups disponibles
./backup_database.sh --list

# Restaurar backup específico
./backup_database.sh --restore /var/www/certificates/backups/backup_certificados_drtc_20240115_020000.sql.gz
```

#### Restaurar Archivos Media

```bash
# Extraer backup de media
tar -xzf /var/www/certificates/backups/media_backup_20240115_020000.tar.gz -C /var/www/certificates/
```

### Seguridad en Producción

#### Checklist de Seguridad

- ✅ `DEBUG=False` en producción
- ✅ `SECRET_KEY` único y seguro
- ✅ HTTPS configurado con certificado válido
- ✅ Firewall configurado (solo puertos 80, 443, 22)
- ✅ PostgreSQL solo acepta conexiones locales
- ✅ Backups automáticos configurados
- ✅ Permisos de archivos correctos
- ✅ Rate limiting activado
- ✅ Headers de seguridad configurados en Nginx

#### Configurar Firewall

```bash
# Instalar UFW
sudo apt install -y ufw

# Configurar reglas
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# Habilitar firewall
sudo ufw enable

# Verificar estado
sudo ufw status
```

#### Hardening de PostgreSQL

```bash
# Editar configuración
sudo nano /etc/postgresql/14/main/postgresql.conf

# Asegurar que solo escucha en localhost
listen_addresses = 'localhost'

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

### Troubleshooting en Producción

#### Servicio no inicia

```bash
# Ver logs detallados
sudo journalctl -u certificates-drtc -n 50

# Verificar configuración
python manage.py check --deploy

# Verificar permisos
ls -la /var/www/certificates
```

#### Error 502 Bad Gateway

```bash
# Verificar que Gunicorn está corriendo
sudo systemctl status certificates-drtc

# Verificar que el socket está escuchando
sudo netstat -tlnp | grep 8000

# Reiniciar servicio
sudo systemctl restart certificates-drtc
```

#### Error de Base de Datos

```bash
# Verificar conexión a PostgreSQL
sudo -u postgres psql -d certificados_drtc

# Verificar credenciales en .env
cat /var/www/certificates/.env | grep DATABASE

# Ver logs de PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

#### Archivos Estáticos no se Cargan

```bash
# Recolectar archivos estáticos
cd /var/www/certificates
source venv/bin/activate
python manage.py collectstatic --noinput

# Verificar permisos
sudo chown -R www-data:www-data /var/www/certificates/staticfiles

# Verificar configuración de Nginx
sudo nginx -t
```

### Performance y Optimización

#### Optimización de Base de Datos

```bash
# Ejecutar VACUUM y ANALYZE
sudo -u postgres psql -d certificados_drtc -c "VACUUM ANALYZE;"

# Crear índices adicionales si es necesario
python manage.py dbshell
```

#### Monitoreo de Recursos

```bash
# Uso de CPU y memoria
htop

# Espacio en disco
df -h

# Tamaño de la base de datos
sudo -u postgres psql -d certificados_drtc -c "SELECT pg_size_pretty(pg_database_size('certificados_drtc'));"

# Tamaño de archivos media
du -sh /var/www/certificates/media/
```

#### Configuración de Workers de Gunicorn

Edita `/etc/systemd/system/certificates-drtc.service`:

```ini
# Fórmula: (2 x CPU cores) + 1
--workers 5  # Para servidor con 2 cores
```

### Documentación Adicional

- [Configuración de Settings](docs/SETTINGS_CONFIGURATION.md)
- [Guía de Administrador](docs/ADMIN_GUIDE.md)
- [Servicio de Firma Digital](docs/DIGITAL_SIGNATURE_SERVICE.md)
- [Comandos de Management](docs/MANAGEMENT_COMMANDS.md)

## Estructura del Proyecto

```
sistema-certificados-drtc/
│
├── config/                          # Configuración del proyecto Django
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py                  # Configuración base común
│   │   ├── development.py           # Configuración de desarrollo
│   │   └── production.py            # Configuración de producción
│   ├── urls.py                      # URLs principales del proyecto
│   ├── wsgi.py                      # Configuración WSGI
│   └── asgi.py                      # Configuración ASGI
│
├── certificates/                    # Aplicación principal
│   ├── management/
│   │   └── commands/                # Comandos personalizados
│   │       ├── load_default_template.py
│   │       ├── generate_certificates.py
│   │       ├── sign_certificates.py
│   │       └── create_superuser_if_not_exists.py
│   ├── migrations/                  # Migraciones de base de datos
│   ├── services/                    # Lógica de negocio
│   │   ├── excel_processor.py       # Procesamiento de Excel
│   │   ├── certificate_generator.py # Generación de certificados
│   │   ├── qr_service.py            # Generación de códigos QR
│   │   └── digital_signature.py     # Integración con firma digital
│   ├── tests/                       # Tests unitarios e integración
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   ├── test_views.py
│   │   └── test_integration.py
│   ├── views/                       # Vistas
│   │   ├── admin_views.py           # Vistas de administración
│   │   └── public_views.py          # Vistas públicas
│   ├── models.py                    # Modelos de datos
│   ├── admin.py                     # Configuración Django Admin
│   ├── forms.py                     # Formularios
│   ├── urls.py                      # URLs de la aplicación
│   └── middleware.py                # Middleware personalizado
│
├── templates/                       # Templates HTML
│   ├── base.html                    # Template base
│   ├── admin/
│   │   └── certificates/
│   │       └── excel_import.html    # Template de importación
│   └── certificates/
│       ├── query.html               # Consulta por DNI
│       ├── results.html             # Resultados de consulta
│       ├── verify.html              # Verificación de certificado
│       └── default_certificate.html # Plantilla de certificado
│
├── static/                          # Archivos estáticos (CSS, JS, imágenes)
│   └── .gitkeep
│
├── media/                           # Archivos subidos (PDFs, QRs)
│   ├── certificates/                # Certificados PDF
│   │   └── YYYY/MM/                 # Organizados por fecha
│   └── qr_codes/                    # Códigos QR
│       └── YYYY/MM/
│
├── logs/                            # Archivos de log
│   ├── certificates.log             # Log general
│   ├── signature.log                # Log de firma digital
│   └── django.log                   # Log de Django
│
├── docs/                            # Documentación adicional
│   ├── POSTGRESQL_SETUP.md
│   ├── PROJECT_STRUCTURE.md
│   ├── SETTINGS_CONFIGURATION.md
│   └── SETUP_COMPLETE.md
│
├── .env                             # Variables de entorno (no en git)
├── .env.example                     # Ejemplo de variables de entorno
├── .gitignore                       # Archivos ignorados por git
├── manage.py                        # Script de gestión de Django
├── requirements.txt                 # Dependencias Python
├── start.bat                        # Script de inicio (Windows)
├── db.sqlite3                       # Base de datos SQLite (desarrollo)
└── README.md                        # Este archivo
```

### Descripción de Componentes Clave

#### Models (certificates/models.py)

- **Event**: Eventos de capacitación
- **Participant**: Participantes de eventos
- **Certificate**: Certificados generados
- **CertificateTemplate**: Plantillas de certificados
- **AuditLog**: Registro de auditoría

#### Services (certificates/services/)

- **ExcelProcessorService**: Procesa archivos Excel e importa participantes
- **CertificateGeneratorService**: Genera certificados PDF con QR
- **QRCodeService**: Genera códigos QR de verificación
- **DigitalSignatureService**: Integración con servicio de firma digital

#### Views

- **Admin Views**: Importación de Excel, gestión de certificados
- **Public Views**: Consulta por DNI, verificación por QR, descarga de certificados

## Testing

### Ejecutar Tests

```bash
# Ejecutar todos los tests
python manage.py test

# Ejecutar tests de una aplicación específica
python manage.py test certificates

# Ejecutar un archivo de test específico
python manage.py test certificates.tests.test_models

# Ejecutar una clase de test específica
python manage.py test certificates.tests.test_models.ParticipantModelTest

# Ejecutar un test específico
python manage.py test certificates.tests.test_models.ParticipantModelTest.test_unique_dni_per_event
```

### Tests con Cobertura

```bash
# Instalar coverage
pip install coverage

# Ejecutar tests con cobertura
coverage run --source='.' manage.py test

# Ver reporte en consola
coverage report

# Generar reporte HTML
coverage html

# Abrir reporte HTML (Windows)
start htmlcov\index.html
```

### Tipos de Tests Incluidos

#### 1. Tests Unitarios

- **Models**: Validaciones, relaciones, métodos
- **Services**: Lógica de negocio aislada
- **Forms**: Validaciones de formularios

#### 2. Tests de Integración

- **Flujo completo**: Importar → Generar → Firmar → Consultar
- **Vistas**: Peticiones HTTP y respuestas
- **Admin**: Acciones personalizadas

#### 3. Tests de Performance

- Importación de archivos grandes
- Generación masiva de certificados
- Consultas con grandes volúmenes de datos

### Ejecutar Tests Específicos

```bash
# Tests de modelos
python manage.py test certificates.tests.test_models

# Tests de servicios
python manage.py test certificates.tests.test_excel_processor
python manage.py test certificates.tests.test_certificate_generator
python manage.py test certificates.tests.test_digital_signature

# Tests de vistas
python manage.py test certificates.tests.test_admin_views
python manage.py test certificates.tests.test_public_views

# Tests de integración
python manage.py test certificates.tests.test_integration
```

## Deployment

### Preparación para Producción

#### 1. Configuración de Entorno

```bash
# Establecer entorno de producción
DJANGO_ENVIRONMENT=production

# Desactivar debug
DEBUG=False

# Configurar hosts permitidos
ALLOWED_HOSTS=certificados.drtcpuno.gob.pe,www.certificados.drtcpuno.gob.pe

# Usar base de datos PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/certificados_drtc

# Generar nueva SECRET_KEY
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
```

#### 2. Instalar Dependencias de Producción

```bash
pip install -r requirements.txt
pip install gunicorn whitenoise
```

#### 3. Configurar Base de Datos

```bash
# Crear base de datos
createdb certificados_drtc

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py create_superuser_if_not_exists

# Cargar plantilla por defecto
python manage.py load_default_template
```

#### 4. Recolectar Archivos Estáticos

```bash
python manage.py collectstatic --noinput
```

#### 5. Verificar Configuración

```bash
# Verificar configuración general
python manage.py check

# Verificar configuración de producción
python manage.py check --deploy
```

### Deployment con Gunicorn

#### 1. Instalar Gunicorn

```bash
pip install gunicorn
```

#### 2. Crear Archivo de Configuración

Crear `gunicorn_config.py`:

```python
import multiprocessing

# Dirección y puerto
bind = "127.0.0.1:8000"

# Número de workers (2-4 x CPU cores)
workers = multiprocessing.cpu_count() * 2 + 1

# Tipo de worker
worker_class = "sync"

# Timeout
timeout = 120

# Logs
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "info"

# Daemon
daemon = False

# PID file
pidfile = "gunicorn.pid"
```

#### 3. Ejecutar Gunicorn

```bash
gunicorn config.wsgi:application -c gunicorn_config.py
```

### Deployment con Nginx

#### 1. Instalar Nginx

```bash
# Ubuntu/Debian
sudo apt-get install nginx

# CentOS/RHEL
sudo yum install nginx
```

#### 2. Configurar Nginx

Crear `/etc/nginx/sites-available/certificados`:

```nginx
upstream certificados_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name certificados.drtcpuno.gob.pe;
    
    # Redirigir a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name certificados.drtcpuno.gob.pe;
    
    # Certificados SSL
    ssl_certificate /etc/letsencrypt/live/certificados.drtcpuno.gob.pe/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/certificados.drtcpuno.gob.pe/privkey.pem;
    
    # Configuración SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Tamaño máximo de upload
    client_max_body_size 10M;
    
    # Logs
    access_log /var/log/nginx/certificados_access.log;
    error_log /var/log/nginx/certificados_error.log;
    
    # Archivos estáticos
    location /static/ {
        alias /var/www/certificados/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Archivos media
    location /media/ {
        alias /var/www/certificados/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # Proxy a Gunicorn
    location / {
        proxy_pass http://certificados_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

#### 3. Habilitar Sitio

```bash
sudo ln -s /etc/nginx/sites-available/certificados /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Deployment con Systemd

#### 1. Crear Servicio Systemd

Crear `/etc/systemd/system/certificados.service`:

```ini
[Unit]
Description=Sistema de Certificados DRTC Gunicorn
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
RuntimeDirectory=gunicorn
WorkingDirectory=/var/www/certificados
Environment="PATH=/var/www/certificados/venv/bin"
EnvironmentFile=/var/www/certificados/.env
ExecStart=/var/www/certificados/venv/bin/gunicorn \
    --config /var/www/certificados/gunicorn_config.py \
    config.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

#### 2. Habilitar y Ejecutar Servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable certificados
sudo systemctl start certificados
sudo systemctl status certificados
```

#### 3. Comandos Útiles

```bash
# Ver logs
sudo journalctl -u certificados -f

# Reiniciar servicio
sudo systemctl restart certificados

# Detener servicio
sudo systemctl stop certificados

# Ver estado
sudo systemctl status certificados
```

### SSL/TLS con Let's Encrypt

```bash
# Instalar Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtener certificado
sudo certbot --nginx -d certificados.drtcpuno.gob.pe

# Renovación automática (ya configurada)
sudo certbot renew --dry-run
```

### Backup y Restore

#### Backup de Base de Datos

```bash
# Backup
pg_dump -U certificados_user certificados_drtc > backup_$(date +%Y%m%d).sql

# Backup comprimido
pg_dump -U certificados_user certificados_drtc | gzip > backup_$(date +%Y%m%d).sql.gz
```

#### Restore de Base de Datos

```bash
# Restore
psql -U certificados_user certificados_drtc < backup_20241028.sql

# Restore desde comprimido
gunzip -c backup_20241028.sql.gz | psql -U certificados_user certificados_drtc
```

#### Backup de Archivos Media

```bash
# Backup
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/

# Restore
tar -xzf media_backup_20241028.tar.gz
```

#### Script de Backup Automático

Crear `backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/var/backups/certificados"
DATE=$(date +%Y%m%d_%H%M%S)

# Crear directorio de backup
mkdir -p $BACKUP_DIR

# Backup de base de datos
pg_dump -U certificados_user certificados_drtc | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup de archivos media
tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C /var/www/certificados media/

# Eliminar backups antiguos (más de 30 días)
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completado: $DATE"
```

Agregar a crontab:

```bash
# Ejecutar backup diario a las 2 AM
0 2 * * * /var/www/certificados/backup.sh
```

## Troubleshooting

### Problemas Comunes

#### 1. Error al Importar Excel

**Síntoma:** Error "Invalid file format" o "Missing columns"

**Solución:**
- Verifica que el archivo sea .xlsx o .xls
- Verifica que las columnas tengan los nombres exactos requeridos
- Asegúrate de que no haya filas vacías al inicio
- Verifica que el archivo no esté corrupto

#### 2. Error al Generar Certificados

**Síntoma:** Error "Template not found" o "PDF generation failed"

**Solución:**
```bash
# Cargar plantilla por defecto
python manage.py load_default_template

# Verificar que WeasyPrint esté instalado correctamente
python -c "import weasyprint; print(weasyprint.__version__)"
```

#### 3. Error de Conexión a Base de Datos

**Síntoma:** "could not connect to server" o "FATAL: password authentication failed"

**Solución:**
- Verifica que PostgreSQL esté ejecutándose
- Verifica las credenciales en `.env`
- Verifica que la base de datos exista
- Verifica los permisos del usuario

```bash
# Verificar estado de PostgreSQL
sudo systemctl status postgresql

# Conectar manualmente
psql -U certificados_user -d certificados_drtc -h localhost
```

#### 4. Error al Firmar Certificados

**Síntoma:** "Connection timeout" o "401 Unauthorized"

**Solución:**
- Verifica la configuración del servicio de firma en `.env`
- Verifica que la API Key sea válida
- Verifica la conectividad con el servicio
- Revisa los logs: `logs/signature.log`

#### 5. Archivos Media No Se Muestran

**Síntoma:** 404 al intentar descargar certificados

**Solución en desarrollo:**
```python
# Verificar en urls.py que esté configurado:
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

**Solución en producción:**
- Verifica la configuración de Nginx para servir archivos media
- Verifica permisos de la carpeta media

```bash
sudo chown -R www-data:www-data /var/www/certificados/media/
sudo chmod -R 755 /var/www/certificados/media/
```

#### 6. Error de Permisos en Logs

**Síntoma:** "Permission denied" al escribir logs

**Solución:**
```bash
# Crear directorio de logs
mkdir -p logs

# Dar permisos
chmod 755 logs
touch logs/certificates.log logs/signature.log logs/django.log
chmod 644 logs/*.log
```

#### 7. Rate Limiting Bloqueando Usuarios

**Síntoma:** "Rate limit exceeded" en consultas públicas

**Solución:**
- Ajustar límites en `views/public_views.py`
- Verificar que la IP del usuario sea correcta (detrás de proxy)
- Limpiar cache de rate limiting

```python
# En views/public_views.py
@ratelimit(key='ip', rate='20/m')  # Aumentar de 10 a 20
```

### Logs y Debugging

#### Ver Logs en Desarrollo

```bash
# Windows
type logs\certificates.log
type logs\signature.log
type logs\django.log

# Linux/Mac
tail -f logs/certificates.log
tail -f logs/signature.log
tail -f logs/django.log
```

#### Ver Logs en Producción

```bash
# Logs de Gunicorn
tail -f logs/gunicorn_error.log
tail -f logs/gunicorn_access.log

# Logs de Nginx
sudo tail -f /var/log/nginx/certificados_error.log
sudo tail -f /var/log/nginx/certificados_access.log

# Logs de Systemd
sudo journalctl -u certificados -f
```

#### Activar Debug Logging

En `.env`:

```bash
LOG_LEVEL=DEBUG
```

Reiniciar el servidor.

### Verificación de Salud del Sistema

```bash
# Verificar configuración
python manage.py check --deploy

# Verificar conexión a base de datos
python manage.py dbshell

# Verificar migraciones pendientes
python manage.py showmigrations

# Verificar archivos estáticos
python manage.py findstatic admin/css/base.css

# Verificar permisos
python manage.py check --deploy
```

## Documentación Adicional

- [Configuración de PostgreSQL](docs/POSTGRESQL_SETUP.md) - Guía detallada de instalación y configuración de PostgreSQL
- [Estructura del Proyecto](docs/PROJECT_STRUCTURE.md) - Descripción detallada de la arquitectura
- [Configuración de Settings](docs/SETTINGS_CONFIGURATION.md) - Explicación de todas las configuraciones
- [Setup Completo](docs/SETUP_COMPLETE.md) - Resumen del setup inicial

## Soporte y Contacto

### Reportar Problemas

Si encuentras un bug o tienes una sugerencia:

1. Verifica que no exista un issue similar
2. Crea un nuevo issue con:
   - Descripción clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Logs relevantes
   - Versión del sistema

### Contribuir

Las contribuciones son bienvenidas:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

### Contacto

- **Email**: soporte@drtcpuno.gob.pe
- **Sitio Web**: https://www.drtcpuno.gob.pe

## Licencia

Este proyecto es propiedad de la Dirección Regional de Transportes y Comunicaciones de Puno.

## Changelog

### Versión 1.0.0 (2024-10-28)

- ✅ Implementación inicial del sistema
- ✅ Importación de participantes desde Excel
- ✅ Generación de certificados PDF con QR
- ✅ Integración con servicio de firma digital
- ✅ Consulta pública por DNI
- ✅ Verificación por código QR
- ✅ Panel de administración completo
- ✅ Sistema de auditoría
- ✅ Rate limiting
- ✅ Logging completo
- ✅ Tests unitarios e integración
- ✅ Documentación completa

---

**Sistema de Certificados DRTC Puno** - Desarrollado para la Dirección Regional de Transportes y Comunicaciones de Puno
#   s i s t e m a _ c e r t i f i c a d o s _ d r t c 
 
 