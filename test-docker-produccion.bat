@echo off
REM Script de prueba con ruta completa de Docker
REM Sistema de Certificados DRTC

SET DOCKER="C:\Program Files\Docker\Docker\resources\bin\docker.exe"

echo ========================================
echo PRUEBA DE PRODUCCION CON DOCKER
echo Sistema de Certificados DRTC
echo ========================================
echo.

echo [1/8] Verificando Docker...
%DOCKER% --version
if errorlevel 1 (
    echo ERROR: Docker no encontrado
    pause
    exit /b 1
)
echo.

echo [2/8] Deteniendo contenedores existentes...
%DOCKER% compose -f docker-compose.prod.yml down
echo.

echo [3/8] Limpiando redes Docker...
%DOCKER% network prune -f
echo.

echo [4/8] Construyendo imagen (esto puede tardar varios minutos)...
%DOCKER% compose -f docker-compose.prod.yml build --no-cache
if errorlevel 1 (
    echo ERROR: Fallo al construir imagen
    pause
    exit /b 1
)
echo.

echo [5/8] Iniciando servicios...
%DOCKER% compose -f docker-compose.prod.yml up -d
if errorlevel 1 (
    echo ERROR: Fallo al iniciar servicios
    pause
    exit /b 1
)
echo.

echo [6/8] Esperando 30 segundos a que servicios estén listos...
timeout /t 30 /nobreak
echo.

echo [7/8] Estado de contenedores:
%DOCKER% compose -f docker-compose.prod.yml ps
echo.

echo [8/8] Logs del contenedor web:
%DOCKER% compose -f docker-compose.prod.yml logs --tail=50 web
echo.

echo ========================================
echo PRUEBA COMPLETADA
echo ========================================
echo.
echo Accede a: http://localhost
echo Admin: http://localhost/admin/
echo.
echo Ver logs: %DOCKER% compose -f docker-compose.prod.yml logs -f web
echo Detener: %DOCKER% compose -f docker-compose.prod.yml down
echo.

pause
