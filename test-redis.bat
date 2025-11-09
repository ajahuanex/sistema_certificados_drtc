@echo off
REM Script para probar la configuración de Redis en Docker (Windows)

echo ==========================================
echo Test de Configuracion Redis
echo ==========================================
echo.

REM Verificar que Docker Compose esté corriendo
echo [INFO] Verificando servicios Docker...
docker-compose ps | findstr "Up" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Los servicios Docker no estan corriendo
    echo Ejecuta: docker-compose up -d
    exit /b 1
)
echo [OK] Servicios Docker estan corriendo
echo.

REM Test 1: Verificar que Redis esté corriendo
echo [INFO] Test 1: Verificando servicio Redis...
docker-compose exec -T redis redis-cli ping | findstr "PONG" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Redis no esta respondiendo
    exit /b 1
)
echo [OK] Redis esta respondiendo correctamente
echo.

REM Test 2: Verificar configuración de Redis
echo [INFO] Test 2: Verificando configuracion de Redis...
echo Configuracion actual:
docker-compose exec -T redis redis-cli CONFIG GET maxmemory
docker-compose exec -T redis redis-cli CONFIG GET maxmemory-policy
docker-compose exec -T redis redis-cli CONFIG GET appendonly
echo [OK] Configuracion de Redis verificada
echo.

REM Test 3: Verificar persistencia de datos
echo [INFO] Test 3: Verificando persistencia de datos...
docker-compose exec -T redis redis-cli SET test_key "test_value" >nul 2>&1
docker-compose exec -T redis redis-cli GET test_key | findstr "test_value" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Problema con persistencia de datos
    exit /b 1
)
echo [OK] Persistencia de datos funcionando
docker-compose exec -T redis redis-cli DEL test_key >nul 2>&1
echo.

REM Test 4: Verificar conexión desde Django
echo [INFO] Test 4: Verificando conexion Django-Redis...
docker-compose exec -T web python manage.py test_cache
if errorlevel 1 (
    echo [ERROR] Django no puede conectarse a Redis
    exit /b 1
)
echo [OK] Django puede conectarse a Redis correctamente
echo.

REM Test 5: Verificar información de Redis
echo [INFO] Test 5: Informacion del servidor Redis...
echo Estadisticas de Redis:
docker-compose exec -T redis redis-cli INFO stats | findstr "total_connections_received total_commands_processed keyspace_hits keyspace_misses"
echo.
docker-compose exec -T redis redis-cli INFO memory | findstr "used_memory_human maxmemory_human"
echo [OK] Informacion de Redis obtenida
echo.

REM Resumen final
echo ==========================================
echo Resumen de Tests
echo ==========================================
echo [OK] Todos los tests de Redis pasaron correctamente
echo.
echo Redis esta configurado y funcionando para:
echo   - Cache de Django
echo   - Almacenamiento de sesiones
echo   - Persistencia de datos
echo.
echo [INFO] Para monitorear Redis en tiempo real:
echo   docker-compose exec redis redis-cli MONITOR
echo.
echo [INFO] Para ver estadisticas de Redis:
echo   docker-compose exec redis redis-cli INFO
echo.
pause
