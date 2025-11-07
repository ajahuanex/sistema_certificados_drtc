@echo off
REM Script de prueba completa para producción - Windows
REM Sistema de Certificados DRTC

echo ========================================
echo PRUEBA COMPLETA DE PRODUCCION
echo Sistema de Certificados DRTC
echo ========================================
echo.

REM Verificar que Docker está instalado
echo [1/8] Verificando Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker no está instalado o no está en el PATH
    echo Por favor instala Docker Desktop desde: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo OK: Docker instalado
echo.

REM Detener contenedores existentes
echo [2/8] Deteniendo contenedores existentes...
docker compose -f docker-compose.prod.yml down
echo.

REM Limpiar red si existe
echo [3/8] Limpiando redes Docker...
docker network prune -f
echo.

REM Construir imágenes sin cache
echo [4/8] Construyendo imagen Docker (esto puede tardar varios minutos)...
docker compose -f docker-compose.prod.yml build --no-cache
if errorlevel 1 (
    echo ERROR: Fallo al construir la imagen
    pause
    exit /b 1
)
echo OK: Imagen construida exitosamente
echo.

REM Iniciar servicios
echo [5/8] Iniciando servicios...
docker compose -f docker-compose.prod.yml up -d
if errorlevel 1 (
    echo ERROR: Fallo al iniciar servicios
    pause
    exit /b 1
)
echo OK: Servicios iniciados
echo.

REM Esperar a que los servicios estén listos
echo [6/8] Esperando a que los servicios estén listos (30 segundos)...
timeout /t 30 /nobreak >nul
echo.

REM Verificar estado de contenedores
echo [7/8] Verificando estado de contenedores...
docker compose -f docker-compose.prod.yml ps
echo.

REM Verificar logs del contenedor web
echo [8/8] Verificando logs del contenedor web...
echo.
echo === ULTIMAS 50 LINEAS DE LOGS ===
docker compose -f docker-compose.prod.yml logs --tail=50 web
echo.

echo ========================================
echo PRUEBA COMPLETADA
echo ========================================
echo.
echo Verifica que todos los contenedores estén "Up" y "healthy"
echo.
echo Accede a la aplicación en:
echo   - http://localhost (Aplicación principal)
echo   - http://localhost/admin/ (Panel de administración)
echo.
echo Para ver logs en tiempo real:
echo   docker compose -f docker-compose.prod.yml logs -f web
echo.
echo Para detener los servicios:
echo   docker compose -f docker-compose.prod.yml down
echo.

pause
