"""
Tests de integración para Docker
Verifica el funcionamiento correcto de la aplicación en contenedores Docker
"""
import os
import time
from django.test import TestCase, LiveServerTestCase, override_settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import connection
from django.conf import settings
import redis
from datetime import date

from certificates.models import Event, Participant, Certificate, CertificateTemplate


class DockerDatabaseConnectionTest(TestCase):
    """Tests para verificar la conexión a PostgreSQL en Docker"""

    def test_database_connection_is_active(self):
        """Verifica que la conexión a la base de datos está activa"""
        self.assertTrue(connection.is_usable())

    def test_database_is_postgresql(self):
        """Verifica que se está usando PostgreSQL en producción"""
        db_engine = settings.DATABASES['default']['ENGINE']
        # En desarrollo puede ser SQLite, en producción debe ser PostgreSQL
        self.assertIn('postgresql', db_engine.lower(), 
                     msg="La base de datos debe ser PostgreSQL en producción")

    def test_database_crud_operations(self):
        """Verifica operaciones CRUD básicas en la base de datos"""
        # Create
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertIsNotNone(user.id)
        
        # Read
        retrieved_user = User.objects.get(username='testuser')
        self.assertEqual(retrieved_user.email, 'test@example.com')
        
        # Update
        retrieved_user.email = 'updated@example.com'
        retrieved_user.save()
        updated_user = User.objects.get(username='testuser')
        self.assertEqual(updated_user.email, 'updated@example.com')
        
        # Delete
        user_id = updated_user.id
        updated_user.delete()
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_database_transactions(self):
        """Verifica que las transacciones funcionan correctamente"""
        from django.db import transaction
        
        initial_count = User.objects.count()
        
        try:
            with transaction.atomic():
                User.objects.create_user(
                    username='transactiontest',
                    password='testpass123'
                )
                # Forzar un error para probar rollback
                raise Exception("Test rollback")
        except Exception:
            pass
        
        # Verificar que el rollback funcionó
        self.assertEqual(User.objects.count(), initial_count)

    def test_database_foreign_key_constraints(self):
        """Verifica que las restricciones de clave foránea funcionan"""
        template = CertificateTemplate.objects.create(
            name="Test Template",
            html_template="<html><body>Test</body></html>",
            is_default=True
        )
        
        event = Event.objects.create(
            name="Test Event",
            event_date=date(2024, 1, 15),
            template=template
        )
        
        participant = Participant.objects.create(
            dni="12345678",
            full_name="Test User",
            event=event,
            attendee_type="ASISTENTE"
        )
        
        # Verificar relaciones
        self.assertEqual(participant.event, event)
        self.assertEqual(event.template, template)
        self.assertIn(participant, event.participants.all())


class DockerRedisConnectionTest(TestCase):
    """Tests para verificar la conexión a Redis en Docker"""

    def setUp(self):
        """Limpiar cache antes de cada test"""
        cache.clear()

    def test_redis_connection_is_active(self):
        """Verifica que la conexión a Redis está activa"""
        try:
            # Intentar una operación simple
            cache.set('test_key', 'test_value', 10)
            value = cache.get('test_key')
            self.assertEqual(value, 'test_value')
        except Exception as e:
            self.fail(f"Redis connection failed: {str(e)}")

    def test_redis_cache_operations(self):
        """Verifica operaciones básicas de cache"""
        # Set
        cache.set('key1', 'value1', 60)
        cache.set('key2', {'nested': 'dict'}, 60)
        cache.set('key3', [1, 2, 3], 60)
        
        # Get
        self.assertEqual(cache.get('key1'), 'value1')
        self.assertEqual(cache.get('key2'), {'nested': 'dict'})
        self.assertEqual(cache.get('key3'), [1, 2, 3])
        
        # Delete
        cache.delete('key1')
        self.assertIsNone(cache.get('key1'))
        
        # Get with default
        self.assertEqual(cache.get('nonexistent', 'default'), 'default')

    def test_redis_cache_expiration(self):
        """Verifica que la expiración de cache funciona"""
        cache.set('expiring_key', 'value', 1)  # 1 segundo
        self.assertEqual(cache.get('expiring_key'), 'value')
        
        time.sleep(2)  # Esperar a que expire
        self.assertIsNone(cache.get('expiring_key'))

    def test_redis_cache_many_operations(self):
        """Verifica operaciones múltiples de cache"""
        data = {
            'key1': 'value1',
            'key2': 'value2',
            'key3': 'value3'
        }
        
        # Set many
        cache.set_many(data, 60)
        
        # Get many
        retrieved = cache.get_many(['key1', 'key2', 'key3'])
        self.assertEqual(retrieved, data)
        
        # Delete many
        cache.delete_many(['key1', 'key2'])
        self.assertIsNone(cache.get('key1'))
        self.assertIsNone(cache.get('key2'))
        self.assertEqual(cache.get('key3'), 'value3')

    def test_redis_session_storage(self):
        """Verifica que las sesiones se almacenan en Redis"""
        from django.contrib.sessions.backends.cache import SessionStore
        
        session = SessionStore()
        session['test_data'] = 'test_value'
        session.save()
        
        session_key = session.session_key
        self.assertIsNotNone(session_key)
        
        # Recuperar sesión
        new_session = SessionStore(session_key=session_key)
        self.assertEqual(new_session.get('test_data'), 'test_value')


class DockerServiceCommunicationTest(TestCase):
    """Tests para verificar la comunicación entre servicios Docker"""

    def test_web_to_database_communication(self):
        """Verifica comunicación entre contenedor web y base de datos"""
        # Crear un registro en la base de datos
        user = User.objects.create_user(
            username='commtest',
            password='testpass123'
        )
        
        # Verificar que se puede leer
        retrieved = User.objects.get(username='commtest')
        self.assertEqual(retrieved.id, user.id)

    def test_web_to_redis_communication(self):
        """Verifica comunicación entre contenedor web y Redis"""
        cache.set('comm_test', 'communication_works', 60)
        value = cache.get('comm_test')
        self.assertEqual(value, 'communication_works')

    def test_database_persistence_after_restart(self):
        """Verifica que los datos persisten en la base de datos"""
        # Crear datos
        template = CertificateTemplate.objects.create(
            name="Persistence Test",
            html_template="<html><body>Test</body></html>",
            is_default=False
        )
        template_id = template.id
        
        # Simular reconexión cerrando y reabriendo conexión
        connection.close()
        
        # Verificar que los datos persisten
        retrieved = CertificateTemplate.objects.get(id=template_id)
        self.assertEqual(retrieved.name, "Persistence Test")

    def test_concurrent_database_access(self):
        """Verifica acceso concurrente a la base de datos"""
        from django.db import transaction
        
        # Crear múltiples registros en transacciones separadas
        for i in range(10):
            with transaction.atomic():
                User.objects.create_user(
                    username=f'concurrent_user_{i}',
                    password='testpass123'
                )
        
        # Verificar que todos se crearon
        count = User.objects.filter(username__startswith='concurrent_user_').count()
        self.assertEqual(count, 10)


class DockerDataPersistenceTest(TestCase):
    """Tests para verificar la persistencia de datos en volúmenes Docker"""

    def test_media_files_persistence(self):
        """Verifica que los archivos media persisten"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        template = CertificateTemplate.objects.create(
            name="Media Test",
            html_template="<html><body>Test</body></html>",
            is_default=False
        )
        
        event = Event.objects.create(
            name="Media Test Event",
            event_date=date(2024, 1, 15),
            template=template
        )
        
        participant = Participant.objects.create(
            dni="12345678",
            full_name="Test User",
            event=event,
            attendee_type="ASISTENTE"
        )
        
        # Crear certificado con archivos
        certificate = Certificate.objects.create(
            participant=participant,
            pdf_file=SimpleUploadedFile("test.pdf", b"PDF content"),
            qr_code=SimpleUploadedFile("test.png", b"PNG content"),
            verification_url="http://test.com/verify/123"
        )
        
        # Verificar que los archivos existen
        self.assertTrue(certificate.pdf_file)
        self.assertTrue(certificate.qr_code)
        
        # Verificar que se pueden leer
        pdf_content = certificate.pdf_file.read()
        self.assertEqual(pdf_content, b"PDF content")
        
        qr_content = certificate.qr_code.read()
        self.assertEqual(qr_content, b"PNG content")

    def test_database_data_persistence(self):
        """Verifica que los datos de la base de datos persisten"""
        # Crear datos complejos con relaciones
        template = CertificateTemplate.objects.create(
            name="Persistence Template",
            html_template="<html><body>{{ full_name }}</body></html>",
            is_default=True
        )
        
        event = Event.objects.create(
            name="Persistence Event",
            event_date=date(2024, 1, 15),
            description="Test event for persistence",
            template=template
        )
        
        participants = []
        for i in range(5):
            participant = Participant.objects.create(
                dni=f"1234567{i}",
                full_name=f"Test User {i}",
                event=event,
                attendee_type="ASISTENTE"
            )
            participants.append(participant)
        
        # Verificar que todo se guardó correctamente
        self.assertEqual(Event.objects.filter(name="Persistence Event").count(), 1)
        self.assertEqual(Participant.objects.filter(event=event).count(), 5)
        
        # Verificar relaciones
        retrieved_event = Event.objects.get(name="Persistence Event")
        self.assertEqual(retrieved_event.participants.count(), 5)
        self.assertEqual(retrieved_event.template.name, "Persistence Template")


class DockerEnvironmentConfigTest(TestCase):
    """Tests para verificar la configuración del entorno Docker"""

    def test_environment_variables_loaded(self):
        """Verifica que las variables de entorno se cargaron correctamente"""
        # Verificar que SECRET_KEY está configurado
        self.assertIsNotNone(settings.SECRET_KEY)
        self.assertNotEqual(settings.SECRET_KEY, '')
        
        # Verificar que DEBUG está configurado
        self.assertIsNotNone(settings.DEBUG)
        
        # Verificar que ALLOWED_HOSTS está configurado
        self.assertIsNotNone(settings.ALLOWED_HOSTS)

    def test_database_configuration(self):
        """Verifica la configuración de la base de datos"""
        db_config = settings.DATABASES['default']
        
        self.assertIn('ENGINE', db_config)
        self.assertIn('NAME', db_config)
        
        # En producción debe tener configuración completa
        if 'postgresql' in db_config['ENGINE']:
            self.assertIn('USER', db_config)
            self.assertIn('HOST', db_config)
            self.assertIn('PORT', db_config)

    def test_cache_configuration(self):
        """Verifica la configuración de cache"""
        cache_config = settings.CACHES['default']
        
        self.assertIn('BACKEND', cache_config)
        
        # En producción debe usar Redis
        if 'redis' in cache_config['BACKEND'].lower():
            self.assertIn('LOCATION', cache_config)

    def test_static_and_media_configuration(self):
        """Verifica la configuración de archivos estáticos y media"""
        self.assertIsNotNone(settings.STATIC_URL)
        self.assertIsNotNone(settings.STATIC_ROOT)
        self.assertIsNotNone(settings.MEDIA_URL)
        self.assertIsNotNone(settings.MEDIA_ROOT)
        
        # Verificar que los directorios existen o se pueden crear
        import os
        self.assertTrue(os.path.exists(settings.MEDIA_ROOT) or 
                       os.access(os.path.dirname(settings.MEDIA_ROOT), os.W_OK))


class DockerHealthCheckTest(TestCase):
    """Tests para verificar los health checks del sistema"""

    def test_database_health_check(self):
        """Verifica el health check de la base de datos"""
        from certificates.views.health_views import database_health_check
        
        result = database_health_check()
        self.assertTrue(result['healthy'])
        self.assertEqual(result['service'], 'database')

    def test_cache_health_check(self):
        """Verifica el health check de Redis/cache"""
        from certificates.views.health_views import cache_health_check
        
        result = cache_health_check()
        self.assertTrue(result['healthy'])
        self.assertEqual(result['service'], 'cache')

    def test_overall_health_check(self):
        """Verifica el health check general del sistema"""
        from django.test import Client
        
        client = Client()
        response = client.get('/health/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('status', data)
        self.assertIn('services', data)
        self.assertEqual(data['status'], 'healthy')


class DockerPerformanceTest(TestCase):
    """Tests de rendimiento en contenedores Docker"""

    def test_database_query_performance(self):
        """Verifica el rendimiento de consultas a la base de datos"""
        import time
        import uuid
        
        # Crear datos de prueba con nombres únicos
        unique_id = str(uuid.uuid4())[:8]
        template = CertificateTemplate.objects.create(
            name=f"Performance Test {unique_id}",
            html_template="<html><body>Test</body></html>",
            is_default=False
        )
        
        event = Event.objects.create(
            name=f"Performance Event {unique_id}",
            event_date=date(2024, 1, 15),
            template=template
        )
        
        # Crear 100 participantes con DNIs únicos
        participants = []
        for i in range(100):
            participants.append(
                Participant(
                    dni=f"PERF{unique_id}{i:03d}",
                    full_name=f"Test User {i}",
                    event=event,
                    attendee_type="ASISTENTE"
                )
            )
        
        # Medir tiempo de inserción masiva
        start_time = time.time()
        Participant.objects.bulk_create(participants)
        insert_time = time.time() - start_time
        
        # Debe completarse en menos de 5 segundos
        self.assertLess(insert_time, 5.0, 
                       f"Bulk insert took {insert_time:.2f}s, should be < 5s")
        
        # Medir tiempo de consulta
        start_time = time.time()
        result = Participant.objects.filter(event=event).count()
        query_time = time.time() - start_time
        
        self.assertEqual(result, 100)
        # Debe completarse en menos de 1 segundo
        self.assertLess(query_time, 1.0,
                       f"Query took {query_time:.2f}s, should be < 1s")

    def test_cache_performance(self):
        """Verifica el rendimiento de operaciones de cache"""
        import time
        
        # Medir tiempo de escritura
        start_time = time.time()
        for i in range(100):
            cache.set(f'perf_key_{i}', f'value_{i}', 60)
        write_time = time.time() - start_time
        
        # Debe completarse en menos de 2 segundos
        self.assertLess(write_time, 2.0,
                       f"Cache writes took {write_time:.2f}s, should be < 2s")
        
        # Medir tiempo de lectura
        start_time = time.time()
        for i in range(100):
            cache.get(f'perf_key_{i}')
        read_time = time.time() - start_time
        
        # Debe completarse en menos de 1 segundo
        self.assertLess(read_time, 1.0,
                       f"Cache reads took {read_time:.2f}s, should be < 1s")
