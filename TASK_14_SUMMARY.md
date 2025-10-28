# Task 14: Implementar Rate Limiting para Vistas Públicas

## Resumen

Se ha implementado exitosamente el rate limiting para las vistas públicas del sistema de certificados, protegiendo contra uso excesivo y ataques de denegación de servicio.

## Cambios Realizados

### 1. Instalación de Dependencias
- ✅ `django-ratelimit>=4.1` ya estaba en requirements.txt
- ✅ Instalado con `pip install django-ratelimit`

### 2. Actualización de Vistas Públicas (`certificates/views/public_views.py`)

#### Decoradores de Rate Limiting Aplicados:
- **CertificateQueryView**: `@ratelimit(key='ip', rate='10/m', method='POST', block=True)`
  - Limita consultas por DNI a 10 solicitudes por minuto por IP
  - Solo aplica al método POST (búsquedas)
  
- **CertificateVerificationView**: `@ratelimit(key='ip', rate='20/m', method='GET', block=True)`
  - Limita verificaciones de certificados a 20 solicitudes por minuto por IP
  - Aplica al método GET (verificación por QR)

#### Handler Personalizado:
```python
def handler429(request, exception=None):
    """Manejador personalizado para errores 429 (Too Many Requests)"""
    return render(
        request,
        'certificates/rate_limit_exceeded.html',
        {
            'message': 'Ha excedido el límite de solicitudes permitidas...'
        },
        status=429
    )
```

### 3. Middleware Personalizado (`certificates/middleware.py`)

Creado `RatelimitMiddleware` para capturar excepciones `Ratelimited` y mostrar página de error personalizada:

```python
class RatelimitMiddleware:
    def process_exception(self, request, exception):
        if isinstance(exception, Ratelimited):
            return render(request, 'certificates/rate_limit_exceeded.html', ...)
```

### 4. Configuración de Settings (`config/settings/base.py`)

Agregado el middleware al final de la lista:
```python
MIDDLEWARE = [
    ...
    'certificates.middleware.RatelimitMiddleware',
]
```

### 5. Configuración de URLs (`config/urls.py`)

Agregado handler personalizado para errores 429:
```python
handler429 = 'certificates.views.public_views.handler429'
```

### 6. Template de Error (`templates/certificates/rate_limit_exceeded.html`)

Creado template Bootstrap con:
- Mensaje de error claro y amigable
- Explicación de la medida de seguridad
- Botón para volver a la página de consulta
- Diseño responsive

### 7. Tests Completos (`certificates/tests/test_rate_limiting.py`)

Implementados 8 tests que verifican:

#### RateLimitingTestCase:
1. ✅ `test_certificate_query_rate_limit` - Verifica límite de 10 requests/min en consultas
2. ✅ `test_certificate_query_rate_limit_get_not_limited` - Verifica que GET no está limitado
3. ✅ `test_certificate_verification_rate_limit` - Verifica límite de 20 requests/min en verificación
4. ✅ `test_rate_limit_different_ips` - Verifica que el límite es por IP
5. ✅ `test_rate_limit_error_message` - Verifica mensaje de error correcto
6. ✅ `test_rate_limit_template_has_back_link` - Verifica enlace de retorno
7. ✅ `test_download_view_not_rate_limited` - Verifica que descarga no está limitada

#### RateLimitMiddlewareTestCase:
8. ✅ `test_middleware_catches_ratelimited_exception` - Verifica que middleware captura excepciones

### Resultado de Tests
```
Ran 8 tests in 0.283s
OK
```

## Características Implementadas

### Seguridad
- ✅ Rate limiting por IP address
- ✅ Límites diferenciados por tipo de operación
- ✅ Bloqueo automático al exceder límites
- ✅ Mensajes de error informativos

### Experiencia de Usuario
- ✅ Página de error amigable y profesional
- ✅ Explicación clara del problema
- ✅ Navegación fácil para volver
- ✅ Diseño responsive con Bootstrap

### Testing
- ✅ Cobertura completa de funcionalidad
- ✅ Tests de límites por IP
- ✅ Tests de diferentes métodos HTTP
- ✅ Tests de middleware
- ✅ Limpieza de cache entre tests

## Configuración de Rate Limits

| Vista | Método | Límite | Razón |
|-------|--------|--------|-------|
| CertificateQueryView | POST | 10/min | Consultas por DNI - operación más costosa |
| CertificateVerificationView | GET | 20/min | Verificación por QR - operación más ligera |
| CertificateDownloadView | - | Sin límite | Descarga de archivos - no requiere protección |

## Archivos Creados/Modificados

### Creados:
- `certificates/middleware.py` - Middleware para manejar rate limiting
- `certificates/tests/test_rate_limiting.py` - Tests completos
- `templates/certificates/rate_limit_exceeded.html` - Template de error
- `TASK_14_SUMMARY.md` - Este documento

### Modificados:
- `certificates/views/public_views.py` - Agregados decoradores y handler
- `config/settings/base.py` - Agregado middleware
- `config/urls.py` - Agregado handler429

## Requisitos Cumplidos

✅ **Requirement 3.1**: Protección de consultas por DNI con rate limiting  
✅ **Requirement 4.1**: Protección de verificación por QR con rate limiting

## Próximos Pasos

El siguiente task pendiente es:
- **Task 15**: Implementar sistema de logging

## Notas Técnicas

- Se usa `django.core.cache.backends.locmem.LocMemCache` en tests para evitar dependencias externas
- El rate limiting se basa en IP del cliente (soporta X-Forwarded-For para proxies)
- Los límites se resetean automáticamente después del período especificado
- El middleware captura excepciones antes de que lleguen al usuario final
