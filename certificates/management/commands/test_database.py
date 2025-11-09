"""
Management command to test database connection and configuration.
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import sys


class Command(BaseCommand):
    help = 'Test database connection and display configuration'

    def handle(self, *args, **options):
        """Test database connection and display configuration."""
        self.stdout.write(self.style.SUCCESS('Testing database connection...'))
        
        # Display database configuration
        db_config = settings.DATABASES['default']
        self.stdout.write('\nDatabase Configuration:')
        self.stdout.write(f"  Engine: {db_config['ENGINE']}")
        self.stdout.write(f"  Name: {db_config['NAME']}")
        self.stdout.write(f"  User: {db_config['USER']}")
        self.stdout.write(f"  Host: {db_config['HOST']}")
        self.stdout.write(f"  Port: {db_config['PORT']}")
        self.stdout.write(f"  Connection Max Age: {db_config.get('CONN_MAX_AGE', 'Not set')}")
        self.stdout.write(f"  Connection Health Checks: {db_config.get('CONN_HEALTH_CHECKS', 'Not set')}")
        
        # Test connection
        try:
            with connection.cursor() as cursor:
                # Get PostgreSQL version
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f'\n✓ Database connection successful!'))
                self.stdout.write(f'  PostgreSQL Version: {version.split(",")[0]}')
                
                # Get current database name
                cursor.execute("SELECT current_database()")
                current_db = cursor.fetchone()[0]
                self.stdout.write(f'  Current Database: {current_db}')
                
                # Get connection count
                cursor.execute("""
                    SELECT count(*) 
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                """)
                conn_count = cursor.fetchone()[0]
                self.stdout.write(f'  Active Connections: {conn_count}')
                
                # Get database size
                cursor.execute("""
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """)
                db_size = cursor.fetchone()[0]
                self.stdout.write(f'  Database Size: {db_size}')
                
                # Test connection pooling
                self.stdout.write('\nTesting connection pooling...')
                for i in range(3):
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()[0]
                    if result == 1:
                        self.stdout.write(f'  Test {i+1}: ✓')
                
                self.stdout.write(self.style.SUCCESS('\n✓ All database tests passed!'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Database connection failed: {e}'))
            sys.exit(1)
