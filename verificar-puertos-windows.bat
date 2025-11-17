@echo off
echo ============================================
echo VERIFICANDO PUERTOS EN WINDOWS
echo ============================================
echo.

set PUERTOS_OCUPADOS=0

echo Verificando puerto 7070 (HTTP)...
netstat -ano | findstr ":7070" > nul
if %errorlevel% equ 0 (
    echo [OCUPADO] Puerto 7070 esta en uso
    netstat -ano | findstr ":7070"
    set PUERTOS_OCUPADOS=1
) else (
    echo [LIBRE] Puerto 7070 esta disponible
)
echo.

echo Verificando puerto 7443 (HTTPS)...
netstat -ano | findstr ":7443" > nul
if %errorlevel% equ 0 (
    echo [OCUPADO] Puerto 7443 esta en uso
    netstat -ano | findstr ":7443"
    set PUERTOS_OCUPADOS=1
) else (
    echo [LIBRE] Puerto 7443 esta disponible
)
echo.

echo Verificando puerto 5433 (PostgreSQL)...
netstat -ano | findstr ":5433" > nul
if %errorlevel% equ 0 (
    echo [OCUPADO] Puerto 5433 esta en uso
    netstat -ano | findstr ":5433"
    set PUERTOS_OCUPADOS=1
) else (
    echo [LIBRE] Puerto 5433 esta disponible
)
echo.

echo Verificando puerto 6380 (Redis)...
netstat -ano | findstr ":6380" > nul
if %errorlevel% equ 0 (
    echo [OCUPADO] Puerto 6380 esta en uso
    netstat -ano | findstr ":6380"
    set PUERTOS_OCUPADOS=1
) else (
    echo [LIBRE] Puerto 6380 esta disponible
)
echo.

echo ============================================
if %PUERTOS_OCUPADOS% equ 1 (
    echo RESULTADO: Algunos puertos estan ocupados
    echo.
    echo Opciones:
    echo 1. Detener contenedores Docker existentes
    echo 2. Cambiar puertos en docker-compose.prod.yml
    echo.
    echo Para detener contenedores:
    echo docker compose -f docker-compose.prod.yml --env-file .env.production down
) else (
    echo RESULTADO: Todos los puertos estan libres
    echo Puedes proceder con el despliegue
)
echo ============================================
echo.
pause
