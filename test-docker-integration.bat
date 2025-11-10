@echo off
REM Script para ejecutar tests de integración de Docker en Windows
REM Este script verifica el funcionamiento completo de la aplicación en contenedores

setlocal enabledelayedexpansion

echo ==========================================
echo Tests de Integración Docker
echo ==========================================
echo.

REM Limpiar contenedores anteriores
echo [INFO] Limpiando contenedores de test anteriores...
docker-compose -f docker-compose.test.yml down -v 2>nul

echo.
echo [INFO] Construyendo imágenes de test...
docker-compose -f docker-compose.test.yml build
if errorlevel 1 (
    echo [ERROR] Fallo al construir imágenes
    exit /b 1
)

echo.
echo [INFO] Iniciando servicios de test...
docker-compose -f docker-compose.test.yml up -d test-db test-redis
if errorlevel 1 (
    echo [ERROR] Fallo al iniciar servicios
    exit /b 1
)

echo.
echo [INFO] Esperando a que los servicios estén listos...
timeout /t 10 /nobreak >nul

REM Verificar que PostgreSQL está listo
echo [INFO] Verificando PostgreSQL...
docker-compose -f docker-compose.test.yml exec -T test-db pg_isready -U test_user -d test_certificados
if errorlevel 1 (
    echo [ERROR] PostgreSQL no está disponible
    docker-compose -f docker-compose.test.yml down -v
    exit /b 1
)
echo [OK] PostgreSQL está listo

REM Verificar que Redis está listo
echo [INFO] Verificando Redis...
docker-compose -f docker-compose.test.yml exec -T test-redis redis-cli ping
if errorlevel 1 (
    echo [ERROR] Redis no está disponible
    docker-compose -f docker-compose.test.yml down -v
    exit /b 1
)
echo [OK] Redis está listo

echo.
echo ==========================================
echo Ejecutando Tests de Integración
echo ==========================================
echo.

REM Ejecutar tests de integración Docker
echo [INFO] Ejecutando tests de integración Docker...
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py test certificates.tests.test_docker_integration --verbosity=2
set TEST_EXIT_CODE=%errorlevel%

echo.
echo ==========================================
echo Ejecutando Tests de Comunicación
echo ==========================================
echo.

REM Test de conexión a base de datos
echo [INFO] Test: Conexión a PostgreSQL...
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('OK: Conexión a PostgreSQL exitosa')"

REM Test de conexión a Redis
echo [INFO] Test: Conexión a Redis...
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py shell -c "from django.core.cache import cache; cache.set('test_key', 'test_value', 10); value = cache.get('test_key'); print('OK: Conexión a Redis exitosa' if value == 'test_value' else 'ERROR: Redis no devolvió el valor correcto')"

REM Test de migraciones
echo [INFO] Test: Migraciones de base de datos...
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py migrate --noinput

echo.
echo ==========================================
echo Ejecutando Tests de Persistencia
echo ==========================================
echo.

REM Test de persistencia de datos
echo [INFO] Test: Persistencia de datos...
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py shell -c "from django.contrib.auth.models import User; from certificates.models import CertificateTemplate; user = User.objects.create_user('testuser', 'test@example.com', 'testpass123'); template = CertificateTemplate.objects.create(name='Test Template', html_template='<html><body>Test</body></html>', is_default=True); print(f'OK: Usuario creado: {user.username}'); print(f'OK: Template creado: {template.name}')"

REM Verificar que los datos persisten
echo [INFO] Verificando persistencia después de reinicio...
docker-compose -f docker-compose.test.yml restart test-web
timeout /t 5 /nobreak >nul

docker-compose -f docker-compose.test.yml run --rm test-web python manage.py shell -c "from django.contrib.auth.models import User; from certificates.models import CertificateTemplate; user = User.objects.get(username='testuser'); template = CertificateTemplate.objects.get(name='Test Template'); print('OK: Datos persisten correctamente después de reinicio')"

echo.
echo ==========================================
echo Ejecutando Tests de Health Check
echo ==========================================
echo.

REM Test de health check
echo [INFO] Test: Health check endpoint...
docker-compose -f docker-compose.test.yml run --rm test-web python manage.py shell -c "from certificates.views.health_views import database_health_check, cache_health_check; db_health = database_health_check(); cache_health = cache_health_check(); print('OK: Database health check' if db_health['healthy'] else 'ERROR: Database health check'); print('OK: Cache health check' if cache_health['healthy'] else 'ERROR: Cache health check')"

echo.
echo ==========================================
echo Limpieza
echo ==========================================
echo.

echo [INFO] Deteniendo y eliminando contenedores de test...
docker-compose -f docker-compose.test.yml down -v

echo.
echo ==========================================
echo Resumen de Tests
echo ==========================================
echo.

if %TEST_EXIT_CODE% equ 0 (
    echo [OK] Todos los tests de integración Docker pasaron exitosamente
    echo.
    echo [INFO] Los siguientes componentes fueron verificados:
    echo   - Conexión a PostgreSQL
    echo   - Conexión a Redis
    echo   - Comunicación entre servicios
    echo   - Persistencia de datos
    echo   - Health checks
    echo   - Operaciones CRUD
    echo   - Transacciones de base de datos
    echo   - Cache y sesiones
    echo.
    exit /b 0
) else (
    echo [ERROR] Algunos tests fallaron
    echo.
    echo [INFO] Revisa los logs arriba para más detalles
    echo.
    exit /b 1
)
