@echo off
REM ========================================
REM DESPLIEGUE A PRODUCCIÓN - COMANDOS ACTUALIZADOS
REM Sistema de Certificados DRTC
REM Docker Compose v2 (sin guión)
REM ========================================

echo.
echo ========================================
echo DESPLIEGUE A PRODUCCIÓN
echo Sistema de Certificados DRTC
echo ========================================
echo.
echo Este script usa Docker Compose v2
echo Sintaxis: docker compose (sin guión)
echo.

REM Verificar Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no está instalado o no está en el PATH
    pause
    exit /b 1
)

echo [OK] Docker detectado
docker --version
echo.

REM Verificar Docker Compose
docker compose version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose v2 no está disponible
    echo.
    echo Asegúrate de tener Docker Desktop actualizado
    echo Docker Desktop 3.4+ incluye Docker Compose v2
    pause
    exit /b 1
)

echo [OK] Docker Compose v2 detectado
docker compose version
echo.

pause

echo.
echo ========================================
echo PASO 1: Detener contenedores anteriores
echo ========================================
echo.

docker compose -f docker-compose.prod.yml down
echo.
echo [OK] Contenedores detenidos
echo.

pause

echo.
echo ========================================
echo PASO 2: Reconstruir imagen web
echo ========================================
echo.
echo Esto puede tomar varios minutos...
echo.

docker compose -f docker-compose.prod.yml build --no-cache web
if errorlevel 1 (
    echo.
    echo [ERROR] Fallo al construir la imagen
    pause
    exit /b 1
)

echo.
echo [OK] Imagen construida exitosamente
echo.

pause

echo.
echo ========================================
echo PASO 3: Iniciar servicios
echo ========================================
echo.

docker compose -f docker-compose.prod.yml up -d
if errorlevel 1 (
    echo.
    echo [ERROR] Fallo al iniciar servicios
    echo.
    echo Ver logs con:
    echo docker compose -f docker-compose.prod.yml logs
    pause
    exit /b 1
)

echo.
echo [OK] Servicios iniciados
echo.

echo Esperando a que los servicios estén listos...
timeout /t 30 /nobreak >nul

echo.
echo ========================================
echo PASO 4: Verificar estado
echo ========================================
echo.

docker compose -f docker-compose.prod.yml ps

echo.
echo ========================================
echo PASO 5: Ver logs
echo ========================================
echo.

echo Mostrando últimas 20 líneas de logs...
echo.
docker compose -f docker-compose.prod.yml logs --tail=20

echo.
echo ========================================
echo DESPLIEGUE COMPLETADO
echo ========================================
echo.

echo [OK] Servicios desplegados exitosamente
echo.
echo Accede a la aplicación en:
echo   - Página principal: http://localhost/
echo   - Admin:            http://localhost/admin/
echo   - Health check:     http://localhost/health/
echo.

set /p OPEN="¿Abrir en navegador? (S/N): "
if /i "%OPEN%"=="S" (
    start http://localhost/
    start http://localhost/admin/
)

echo.
echo Comandos útiles:
echo   - Ver logs:    docker compose -f docker-compose.prod.yml logs -f
echo   - Ver estado:  docker compose -f docker-compose.prod.yml ps
echo   - Reiniciar:   docker compose -f docker-compose.prod.yml restart
echo   - Detener:     docker compose -f docker-compose.prod.yml stop
echo.

pause
