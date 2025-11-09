"""
Management command to test cache connection and configuration.
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
import sys
import time


class Command(BaseCommand):
    help = 'Test cache connection and display configuration'

    def handle(self, *args, **options):
        """Test cache connection and display configuration."""
        self.stdout.write(self.style.SUCCESS('Testing cache connection...'))
        
        # Display cache configuration
        cache_config = settings.CACHES['default']
        self.stdout.write('\nCache Configuration:')
        self.stdout.write(f"  Backend: {cache_config['BACKEND']}")
        self.stdout.write(f"  Location: {cache_config['LOCATION']}")
        self.stdout.write(f"  Key Prefix: {cache_config.get('KEY_PREFIX', 'Not set')}")
        self.stdout.write(f"  Default Timeout: {cache_config.get('TIMEOUT', 'Not set')} seconds")
        
        # Test basic cache operations
        try:
            self.stdout.write('\nTesting cache operations...')
            
            # Test SET
            test_key = 'test_cache_key'
            test_value = 'test_cache_value'
            cache.set(test_key, test_value, 60)
            self.stdout.write('  SET operation: ✓')
            
            # Test GET
            retrieved_value = cache.get(test_key)
            if retrieved_value == test_value:
                self.stdout.write('  GET operation: ✓')
            else:
                raise Exception(f'Cache value mismatch: expected {test_value}, got {retrieved_value}')
            
            # Test DELETE
            cache.delete(test_key)
            deleted_value = cache.get(test_key)
            if deleted_value is None:
                self.stdout.write('  DELETE operation: ✓')
            else:
                raise Exception('Cache delete failed')
            
            # Test multiple keys
            cache.set_many({
                'key1': 'value1',
                'key2': 'value2',
                'key3': 'value3'
            }, 60)
            values = cache.get_many(['key1', 'key2', 'key3'])
            if len(values) == 3:
                self.stdout.write('  SET_MANY operation: ✓')
                self.stdout.write('  GET_MANY operation: ✓')
            
            # Test cache performance
            self.stdout.write('\nTesting cache performance...')
            start_time = time.time()
            for i in range(100):
                cache.set(f'perf_test_{i}', f'value_{i}', 60)
            set_time = time.time() - start_time
            self.stdout.write(f'  100 SET operations: {set_time:.3f} seconds')
            
            start_time = time.time()
            for i in range(100):
                cache.get(f'perf_test_{i}')
            get_time = time.time() - start_time
            self.stdout.write(f'  100 GET operations: {get_time:.3f} seconds')
            
            # Cleanup
            cache.delete_many([f'perf_test_{i}' for i in range(100)])
            cache.delete_many(['key1', 'key2', 'key3'])
            
            self.stdout.write(self.style.SUCCESS('\n✓ All cache tests passed!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Cache test failed: {e}'))
            sys.exit(1)
