@echo off
REM Script de Actualización para Windows - Sistema de Certificados DRTC

setlocal enabledelayedexpansion

REM Configuración
set APP_DIR=%CD%
set BACKUP_DIR=%APP_DIR%\backups
set LOG_FILE=%APP_DIR%\logs\update.log
set COMPOSE_FILE=docker-compose.prod.yml

REM Crear directorio de logs si no existe
if not exist "%APP_DIR%\logs" mkdir "%APP_DIR%\logs"

echo [%date% %time%] Iniciando proceso de actualizacion >> "%LOG_FILE%"

echo.
echo ==========================================
echo 🚀 Sistema de Actualizacion Automatica
echo    DRTC Certificados
echo ==========================================
echo.

REM Verificar prerrequisitos
echo 🔄 Verificando prerrequisitos...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no esta instalado
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose no esta instalado
    exit /b 1
)

git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git no esta instalado
    exit /b 1
)

if not exist "%COMPOSE_FILE%" (
    echo ❌ Archivo %COMPOSE_FILE% no encontrado
    exit /b 1
)

echo ✅ Prerrequisitos verificados

REM Verificar actualizaciones
echo.
echo 🔄 Verificando actualizaciones en GitHub...
git fetch origin

for /f %%i in ('git rev-parse HEAD') do set LOCAL=%%i
for /f %%i in ('git rev-parse origin/main') do set REMOTE=%%i

if "%LOCAL%"=="%REMOTE%" (
    echo ✅ El codigo ya esta actualizado
    echo No hay actualizaciones disponibles
    pause
    exit /b 0
)

echo ✅ Nuevas actualizaciones disponibles
echo.
echo 📋 Cambios a aplicar:
git log --oneline %LOCAL%..%REMOTE%
echo.

REM Crear backup
echo 🔄 Creando backup de la base de datos...
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set mydate=%%c%%a%%b
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set mytime=%%a%%b
set BACKUP_FILE=%BACKUP_DIR%\backup_%mydate%_%mytime%.sql

docker-compose -f "%COMPOSE_FILE%" exec -T db pg_dump -U certificados_user certificados_prod > "%BACKUP_FILE%"
if errorlevel 1 (
    echo ❌ Error creando backup
    exit /b 1
)
echo ✅ Backup creado: %BACKUP_FILE%

REM Actualizar código
echo.
echo 🔄 Actualizando codigo desde GitHub...
git pull origin main
if errorlevel 1 (
    echo ❌ Error actualizando codigo
    exit /b 1
)
echo ✅ Codigo actualizado desde GitHub

REM Actualizar servicios Docker
echo.
echo 🔄 Actualizando servicios Docker...
echo Deteniendo servicios...
docker-compose -f "%COMPOSE_FILE%" down

echo Reconstruyendo imagenes...
docker-compose -f "%COMPOSE_FILE%" build --no-cache

echo Iniciando servicios...
docker-compose -f "%COMPOSE_FILE%" up -d

echo ✅ Servicios Docker actualizados

REM Ejecutar migraciones
echo.
echo 🔄 Ejecutando migraciones de base de datos...
timeout /t 5 /nobreak >nul
docker-compose -f "%COMPOSE_FILE%" exec -T web python manage.py migrate
if errorlevel 1 (
    echo ❌ Error ejecutando migraciones
    exit /b 1
)
echo ✅ Migraciones ejecutadas correctamente

REM Recopilar archivos estáticos
echo.
echo 🔄 Recopilando archivos estaticos...
docker-compose -f "%COMPOSE_FILE%" exec -T web python manage.py collectstatic --noinput
if errorlevel 1 (
    echo ❌ Error recopilando archivos estaticos
    exit /b 1
)
echo ✅ Archivos estaticos recopilados

REM Verificar salud del sistema
echo.
echo 🔄 Verificando salud de los servicios...
timeout /t 10 /nobreak >nul

REM Verificar servicios
docker-compose -f "%COMPOSE_FILE%" ps

REM Verificar endpoint de salud
curl -f -s http://localhost/health/ >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Endpoint de salud no responde (puede ser normal durante el inicio)
    timeout /t 10 /nobreak >nul
    curl -f -s http://localhost/health/ >nul 2>&1
    if errorlevel 1 (
        echo ❌ Endpoint de salud: FALLO
        echo.
        echo ¿Desea hacer rollback? (S/N)
        set /p response=
        if /i "!response!"=="S" (
            echo 🔄 Iniciando rollback...
            git reset --hard HEAD~1
            docker-compose -f "%COMPOSE_FILE%" down
            docker-compose -f "%COMPOSE_FILE%" up -d --build
            echo ⚠️  Rollback completado
        )
        exit /b 1
    )
)

echo ✅ Endpoint de salud: OK

REM Limpiar Docker
echo.
echo 🔄 Limpiando sistema Docker...
docker image prune -f
docker volume prune -f
echo ✅ Sistema Docker limpiado

echo.
echo ✅ ¡Actualizacion completada exitosamente!
echo [%date% %time%] Actualizacion completada exitosamente >> "%LOG_FILE%"

echo.
echo Presione cualquier tecla para continuar...
pause >nul