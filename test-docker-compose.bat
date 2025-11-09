@echo off
REM Script para probar la configuración de Docker Compose
REM Verifica que todos los servicios estén funcionando correctamente

echo ==========================================
echo Test de Docker Compose - Desarrollo
echo ==========================================
echo.

REM Test 1: Verificar que docker-compose.yml existe
echo Test 1: Verificando archivos de configuración...
if exist "docker-compose.yml" (
    echo [OK] docker-compose.yml existe
) else (
    echo [ERROR] docker-compose.yml no encontrado
    exit /b 1
)

if exist "docker-compose.prod.yml" (
    echo [OK] docker-compose.prod.yml existe
) else (
    echo [ERROR] docker-compose.prod.yml no encontrado
    exit /b 1
)

REM Test 2: Validar sintaxis de Docker Compose
echo.
echo Test 2: Validando sintaxis de Docker Compose...
docker-compose -f docker-compose.yml config >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] docker-compose.yml tiene sintaxis válida
) else (
    echo [ERROR] docker-compose.yml tiene errores de sintaxis
    exit /b 1
)

docker-compose -f docker-compose.prod.yml config >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] docker-compose.prod.yml tiene sintaxis válida
) else (
    echo [ERROR] docker-compose.prod.yml tiene errores de sintaxis
    exit /b 1
)

REM Test 3: Verificar servicios definidos
echo.
echo Test 3: Verificando servicios definidos...
docker-compose -f docker-compose.yml config --services | findstr /C:"web" >nul
if %errorlevel% equ 0 (
    echo [OK] Servicio 'web' definido en desarrollo
) else (
    echo [ERROR] Servicio 'web' no encontrado en desarrollo
    exit /b 1
)

docker-compose -f docker-compose.yml config --services | findstr /C:"db" >nul
if %errorlevel% equ 0 (
    echo [OK] Servicio 'db' definido en desarrollo
) else (
    echo [ERROR] Servicio 'db' no encontrado en desarrollo
    exit /b 1
)

docker-compose -f docker-compose.yml config --services | findstr /C:"redis" >nul
if %errorlevel% equ 0 (
    echo [OK] Servicio 'redis' definido en desarrollo
) else (
    echo [ERROR] Servicio 'redis' no encontrado en desarrollo
    exit /b 1
)

docker-compose -f docker-compose.prod.yml config --services | findstr /C:"nginx" >nul
if %errorlevel% equ 0 (
    echo [OK] Servicio 'nginx' definido en producción
) else (
    echo [ERROR] Servicio 'nginx' no encontrado en producción
    exit /b 1
)

REM Test 4: Verificar volúmenes persistentes
echo.
echo Test 4: Verificando volúmenes persistentes...
docker-compose -f docker-compose.yml config --volumes | findstr /C:"postgres_data_dev" >nul
if %errorlevel% equ 0 (
    echo [OK] Volumen 'postgres_data_dev' definido
) else (
    echo [ERROR] Volumen 'postgres_data_dev' no encontrado
    exit /b 1
)

docker-compose -f docker-compose.yml config --volumes | findstr /C:"redis_data_dev" >nul
if %errorlevel% equ 0 (
    echo [OK] Volumen 'redis_data_dev' definido
) else (
    echo [ERROR] Volumen 'redis_data_dev' no encontrado
    exit /b 1
)

docker-compose -f docker-compose.prod.yml config --volumes | findstr /C:"postgres_data_prod" >nul
if %errorlevel% equ 0 (
    echo [OK] Volumen 'postgres_data_prod' definido
) else (
    echo [ERROR] Volumen 'postgres_data_prod' no encontrado
    exit /b 1
)

REM Test 5: Verificar health checks
echo.
echo Test 5: Verificando health checks...
docker-compose -f docker-compose.yml config | findstr /C:"healthcheck:" >nul
if %errorlevel% equ 0 (
    echo [OK] Health checks definidos en desarrollo
) else (
    echo [ERROR] No se encontraron health checks en desarrollo
    exit /b 1
)

docker-compose -f docker-compose.prod.yml config | findstr /C:"healthcheck:" >nul
if %errorlevel% equ 0 (
    echo [OK] Health checks definidos en producción
) else (
    echo [ERROR] No se encontraron health checks en producción
    exit /b 1
)

REM Test 6: Verificar redes
echo.
echo Test 6: Verificando configuración de redes...
docker-compose -f docker-compose.yml config | findstr /C:"certificados_network" >nul
if %errorlevel% equ 0 (
    echo [OK] Red personalizada configurada en desarrollo
) else (
    echo [ERROR] Red personalizada no encontrada en desarrollo
    exit /b 1
)

docker-compose -f docker-compose.prod.yml config | findstr /C:"certificados_network" >nul
if %errorlevel% equ 0 (
    echo [OK] Red personalizada configurada en producción
) else (
    echo [ERROR] Red personalizada no encontrada en producción
    exit /b 1
)

echo.
echo ==========================================
echo [OK] Todos los tests pasaron exitosamente!
echo ==========================================
echo.
echo Para iniciar el entorno de desarrollo:
echo   docker-compose up -d
echo.
echo Para iniciar el entorno de producción:
echo   docker-compose -f docker-compose.prod.yml up -d
echo.

exit /b 0
