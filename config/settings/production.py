"""
Production settings for config project.
"""
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
# Override the default from base.py with a required environment variable
SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# CSRF Trusted Origins - Para evitar error 403 en formularios
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

# Database Configuration with Connection Pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT', default='5432'),
        # Connection pooling - mantener conexiones abiertas por 10 minutos
        'CONN_MAX_AGE': env.int('DB_CONN_MAX_AGE', default=600),
        # Opciones adicionales de PostgreSQL
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',  # 30 segundos timeout para queries
        },
        # Configuración de pool de conexiones
        'ATOMIC_REQUESTS': True,  # Envolver cada request en una transacción
        'AUTOCOMMIT': True,
        'CONN_HEALTH_CHECKS': True,  # Verificar salud de conexiones antes de usarlas
    }
}

# Cache Configuration - Conditional Redis/Memory based on USE_REDIS
USE_REDIS = env.bool('USE_REDIS', default=True)

if USE_REDIS:
    try:
        # Verificar si django_redis está disponible
        import django_redis
        
        # Redis Cache Configuration
        CACHES = {
            'default': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': env('REDIS_URL', default='redis://redis:6379/0'),
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                    'CONNECTION_POOL_KWARGS': {
                        'max_connections': 50,
                        'retry_on_timeout': True,
                    },
                    'SOCKET_CONNECT_TIMEOUT': 5,
                    'SOCKET_TIMEOUT': 5,
                    # HiredisParser removido - no está disponible en el contenedor
                    'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
                },
                'KEY_PREFIX': env('CACHE_KEY_PREFIX', default='certificados_prod'),
                'TIMEOUT': env.int('CACHE_TIMEOUT', default=3600),  # 1 hora por defecto en producción
            }
        }
        
        # Session Configuration with Redis
        SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
        SESSION_CACHE_ALIAS = 'default'
        
    except ImportError:
        # Fallback a memoria si django_redis no está disponible
        print("WARNING: django_redis no disponible, usando cache en memoria")
        USE_REDIS = False

if not USE_REDIS:
    # Memory Cache Configuration (fallback when Redis is not available)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'certificados-cache',
            'TIMEOUT': env.int('CACHE_TIMEOUT', default=3600),
            'OPTIONS': {
                'MAX_ENTRIES': 1000,
                'CULL_FREQUENCY': 3,
            }
        }
    }
    
    # Session Configuration with Database (fallback when Redis is not available)
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Security settings
# SSL redirect deshabilitado para pruebas locales - habilitar en producción real con HTTPS
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=False)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
# HSTS deshabilitado para pruebas locales - habilitar en producción real
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False)
SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=False)
# Desactivar COOP para HTTP (solo funciona con HTTPS)
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

# Configuración para proxy inverso (Nginx Proxy Manager)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Static files with WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@drtc.gob.do')

# Digital Signature Service Configuration
SIGNATURE_SERVICE_URL = env('SIGNATURE_SERVICE_URL', default='')
SIGNATURE_API_KEY = env('SIGNATURE_API_KEY', default='')
SIGNATURE_TIMEOUT = env.int('SIGNATURE_TIMEOUT', default=30)

# Logging - Solo consola para evitar problemas de permisos en Docker
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'certificates': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'certificates.signature': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
