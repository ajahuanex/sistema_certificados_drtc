#!/usr/bin/env python
"""
Script para probar la configuración de cache condicional
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.conf import settings
from django.core.cache import cache

def test_cache_configuration():
    """Probar la configuración actual de cache"""
    print("=== CONFIGURACIÓN DE CACHE ===")
    print(f"USE_REDIS: {getattr(settings, 'USE_REDIS', 'No definido')}")
    print(f"Cache Backend: {settings.CACHES['default']['BACKEND']}")
    print(f"Session Engine: {settings.SESSION_ENGINE}")
    
    # Probar operaciones básicas de cache
    print("\n=== PRUEBA DE OPERACIONES DE CACHE ===")
    try:
        # Escribir en cache
        cache.set('test_key', 'test_value', 60)
        print("✓ Cache SET exitoso")
        
        # Leer de cache
        value = cache.get('test_key')
        if value == 'test_value':
            print("✓ Cache GET exitoso")
        else:
            print("✗ Cache GET falló")
            
        # Eliminar de cache
        cache.delete('test_key')
        print("✓ Cache DELETE exitoso")
        
        # Verificar que se eliminó
        value = cache.get('test_key')
        if value is None:
            print("✓ Verificación de eliminación exitosa")
        else:
            print("✗ Verificación de eliminación falló")
            
        print("\n✅ Todas las operaciones de cache funcionan correctamente")
        
    except Exception as e:
        print(f"\n❌ Error en operaciones de cache: {e}")
        return False
        
    return True

if __name__ == '__main__':
    success = test_cache_configuration()
    sys.exit(0 if success else 1)