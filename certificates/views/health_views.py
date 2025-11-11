"""
Health check views for monitoring system status.
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.views.decorators.http import require_GET
from django.views.decorators.cache import never_cache
import logging

logger = logging.getLogger(__name__)


def database_health_check():
    """
    Helper function to check database health.
    Returns dict with health status.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return {
            'healthy': True,
            'service': 'database',
            'status': 'ok'
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            'healthy': False,
            'service': 'database',
            'status': 'error',
            'error': str(e)
        }


def cache_health_check():
    """
    Helper function to check cache health.
    Returns dict with health status.
    """
    try:
        cache.set('health_check', 'ok', 10)
        cache_value = cache.get('health_check')
        if cache_value == 'ok':
            return {
                'healthy': True,
                'service': 'cache',
                'status': 'ok'
            }
        else:
            return {
                'healthy': False,
                'service': 'cache',
                'status': 'error',
                'error': 'Cache value mismatch'
            }
    except Exception as e:
        logger.error(f"Cache health check failed: {e}")
        return {
            'healthy': False,
            'service': 'cache',
            'status': 'error',
            'error': str(e)
        }


@require_GET
@never_cache
def health_check(request):
    """
    Health check endpoint para verificar el estado del sistema.
    Verifica conectividad con base de datos y cache.
    """
    # Use helper functions
    db_health = database_health_check()
    cache_health_result = cache_health_check()
    
    # Build response with services array
    services = {
        'database': db_health,
        'cache': cache_health_result
    }
    
    # Determine overall status
    all_healthy = db_health['healthy'] and cache_health_result['healthy']
    
    status = {
        'status': 'healthy' if all_healthy else 'unhealthy',
        'services': services
    }
    
    # Return appropriate status code
    status_code = 200 if all_healthy else 503
    
    return JsonResponse(status, status=status_code)


@require_GET
@never_cache
def database_check(request):
    """
    Endpoint específico para verificar solo la base de datos.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            db_version = cursor.fetchone()[0]
        
        return JsonResponse({
            'status': 'ok',
            'database': 'postgresql',
            'version': db_version
        })
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=503)


@require_GET
@never_cache
def cache_check(request):
    """
    Endpoint específico para verificar solo el cache.
    """
    try:
        test_key = 'cache_check_test'
        test_value = 'working'
        
        cache.set(test_key, test_value, 10)
        retrieved_value = cache.get(test_key)
        
        if retrieved_value == test_value:
            return JsonResponse({
                'status': 'ok',
                'cache': 'redis'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'error': 'Cache value mismatch'
            }, status=503)
    except Exception as e:
        logger.error(f"Cache check failed: {e}")
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=503)
