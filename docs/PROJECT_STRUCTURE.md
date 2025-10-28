# Estructura del Proyecto

## Descripción General

Este proyecto sigue las mejores prácticas de Django con una estructura modular y escalable.

## Estructura de Directorios

```
sistema-certificados-drtc/
│
├── config/                          # Configuración principal del proyecto
│   ├── settings/                    # Settings modulares
│   │   ├── __init__.py             # Selector de entorno
│   │   ├── base.py                 # Configuración base común
│   │   ├── development.py          # Configuración de desarrollo
│   │   └── production.py           # Configuración de producción
│   ├── __init__.py
│   ├── asgi.py                     # Configuración ASGI
│   ├── urls.py                     # URLs principales
│   └── wsgi.py                     # Configuración WSGI
│
├── certificates/                    # Aplicación principal
│   ├── migrations/                 # Migraciones de base de datos
│   ├── __init__.py
│   ├── admin.py                    # Configuración del admin
│   ├── apps.py                     # Configuración de la app
│   ├── models.py                   # Modelos de datos
│   ├── views.py                    # Vistas
│   └── tests.py                    # Tests
│
├── static/                         # Archivos estáticos (CSS, JS, imágenes)
│   └── .gitkeep
│
├── media/                          # Archivos subidos por usuarios
│   └── .gitkeep
│
├── templates/                      # Templates HTML globales
│   └── .gitkeep
│
├── logs/                           # Logs de la aplicación
│   └── .gitkeep
│
├── docs/                           # Documentación
│   ├── POSTGRESQL_SETUP.md        # Guía de configuración de PostgreSQL
│   └── PROJECT_STRUCTURE.md       # Este archivo
│
├── .env                            # Variables de entorno (no en git)
├── .env.example                    # Ejemplo de variables de entorno
├── .gitignore                      # Archivos ignorados por git
├── manage.py                       # Script de gestión de Django
├── README.md                       # Documentación principal
└── requirements.txt                # Dependencias de Python
```

## Configuración Modular de Settings

El proyecto utiliza una estructura modular para los settings:

### base.py
Contiene la configuración común a todos los entornos:
- Aplicaciones instaladas
- Middleware
- Templates
- Configuración de archivos estáticos y media
- Internacionalización
- Validadores de contraseña

### development.py
Configuración específica para desarrollo:
- DEBUG = True
- Base de datos SQLite (o PostgreSQL si está configurado)
- Email backend de consola
- ALLOWED_HOSTS permisivo

### production.py
Configuración específica para producción:
- DEBUG = False
- Base de datos PostgreSQL
- Configuraciones de seguridad (SSL, HSTS, cookies seguras)
- WhiteNoise para archivos estáticos
- Email backend SMTP
- Logging a archivos

## Variables de Entorno

El proyecto usa `django-environ` para gestionar variables de entorno.

### Variables Principales

- `DJANGO_ENVIRONMENT`: Entorno actual (development/production)
- `SECRET_KEY`: Clave secreta de Django
- `DEBUG`: Modo debug
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Configuración de base de datos
- `ALLOWED_HOSTS`: Hosts permitidos (producción)
- `EMAIL_*`: Configuración de email

## Aplicaciones

### certificates
Aplicación principal que gestiona:
- Modelos de certificados
- Vistas para emisión y consulta
- API para integración con DRTC
- Generación de PDFs y códigos QR

## Archivos Estáticos y Media

### Static Files
- Ubicación de desarrollo: `static/`
- Ubicación de producción: `staticfiles/` (generado por collectstatic)
- URL: `/static/`

### Media Files
- Ubicación: `media/`
- URL: `/media/`
- Contiene archivos subidos por usuarios (logos, firmas, etc.)

## Base de Datos

### Desarrollo
Por defecto usa SQLite para facilitar el desarrollo en Windows.
Se puede cambiar a PostgreSQL siguiendo la guía en `docs/POSTGRESQL_SETUP.md`.

### Producción
Usa PostgreSQL con configuración optimizada:
- Connection pooling
- Configuración de seguridad
- Backups automáticos (configurar externamente)

## Seguridad

### Desarrollo
- DEBUG activado
- SECRET_KEY por defecto
- Cookies no seguras
- Sin SSL

### Producción
- DEBUG desactivado
- SECRET_KEY desde variable de entorno
- Cookies seguras (SECURE, HTTPONLY)
- SSL/HTTPS obligatorio
- HSTS habilitado
- Protección XSS y clickjacking

## Logging

### Desarrollo
Los logs se muestran en consola.

### Producción
Los logs se guardan en:
- `logs/django.log`: Errores y warnings
- Consola: Información general

## Testing

Los tests se ejecutan con:
```bash
python manage.py test
```

Los tests deben estar en:
- `certificates/tests.py` o
- `certificates/tests/` (para múltiples archivos)

## Deployment

Para desplegar en producción:

1. Configurar variables de entorno en `.env`
2. Establecer `DJANGO_ENVIRONMENT=production`
3. Configurar PostgreSQL
4. Ejecutar migraciones: `python manage.py migrate`
5. Recolectar estáticos: `python manage.py collectstatic`
6. Usar gunicorn: `gunicorn config.wsgi:application`
7. Configurar nginx como reverse proxy

## Mejores Prácticas

1. **Nunca** commitear el archivo `.env`
2. Usar `.env.example` como plantilla
3. Mantener las dependencias actualizadas
4. Escribir tests para nueva funcionalidad
5. Usar migraciones para cambios en la base de datos
6. Documentar cambios importantes
7. Seguir PEP 8 para código Python
8. Usar nombres descriptivos en español para el dominio del negocio
