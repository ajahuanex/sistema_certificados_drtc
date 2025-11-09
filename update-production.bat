@echo off
REM Script de Actualización para Windows - Sistema de Certificados DRTC

setlocal enabledelayedexpansion

REM Configuración
set APP_DIR=%CD%
set BACKUP_DIR=%APP_DIR%\backups
set LOG_FILE=%APP_DIR%\logs\update.log
set COMPOSE_FILE=docker-compose.prod.yml
set ROLLBACK_ENABLED=true
set AUTO_ROLLBACK=true
set HEALTH_CHECK_RETRIES=3
set HEALTH_CHECK_DELAY=10

REM Variables de estado
set CURRENT_COMMIT=
set PREVIOUS_COMMIT=
set BACKUP_FILE=
set DEPLOYMENT_FAILED=false

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

REM Guardar commit actual
for /f %%i in ('git rev-parse HEAD') do set PREVIOUS_COMMIT=%%i
echo [%date% %time%] Commit actual: %PREVIOUS_COMMIT% >> "%LOG_FILE%"

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
    if "%AUTO_ROLLBACK%"=="true" (
        call :perform_rollback "Error al actualizar codigo desde GitHub"
    )
    exit /b 1
)
echo ✅ Codigo actualizado desde GitHub

REM Guardar nuevo commit
for /f %%i in ('git rev-parse HEAD') do set CURRENT_COMMIT=%%i
echo [%date% %time%] Nuevo commit: %CURRENT_COMMIT% >> "%LOG_FILE%"

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
    if "%AUTO_ROLLBACK%"=="true" (
        call :perform_rollback "Error al ejecutar migraciones de base de datos"
    )
    exit /b 1
)
echo ✅ Migraciones ejecutadas correctamente

REM Recopilar archivos estáticos
echo.
echo 🔄 Recopilando archivos estaticos...
docker-compose -f "%COMPOSE_FILE%" exec -T web python manage.py collectstatic --noinput
if errorlevel 1 (
    echo ❌ Error recopilando archivos estaticos
    if "%AUTO_ROLLBACK%"=="true" (
        call :perform_rollback "Error al recopilar archivos estaticos"
    )
    exit /b 1
)
echo ✅ Archivos estaticos recopilados

REM Verificar salud del sistema
echo.
echo 🔄 Verificando salud de los servicios...
call :check_health
if errorlevel 1 (
    echo ❌ Health check fallo
    if "%AUTO_ROLLBACK%"=="true" (
        call :perform_rollback "Health check fallo despues de la actualizacion"
    )
    exit /b 1
)

REM Verificar integridad de la aplicación
echo.
echo 🔄 Verificando integridad de la aplicacion...
call :check_application_integrity
if errorlevel 1 (
    echo ❌ Verificacion de integridad fallo
    if "%AUTO_ROLLBACK%"=="true" (
        call :perform_rollback "Verificacion de integridad de la aplicacion fallo"
    )
    exit /b 1
)

REM Limpiar Docker
echo.
echo 🔄 Limpiando sistema Docker...
docker image prune -f
docker volume prune -f
echo ✅ Sistema Docker limpiado

echo.
echo ==========================================
echo ✅ ACTUALIZACION COMPLETADA EXITOSAMENTE
echo ==========================================
echo Commit anterior: %PREVIOUS_COMMIT%
echo Commit actual: %CURRENT_COMMIT%
echo Backup disponible: %BACKUP_FILE%
echo ==========================================
echo [%date% %time%] Actualizacion completada exitosamente >> "%LOG_FILE%"
call :send_notification "SUCCESS" "Sistema actualizado correctamente de %PREVIOUS_COMMIT% a %CURRENT_COMMIT%"

echo.
echo Presione cualquier tecla para continuar...
pause >nul
exit /b 0

REM ==========================================
REM FUNCIONES
REM ==========================================

:check_health
echo Verificando salud de los servicios...
set /a retry=0

:health_retry
timeout /t %HEALTH_CHECK_DELAY% /nobreak >nul

REM Verificar servicios Docker
docker-compose -f "%COMPOSE_FILE%" ps | findstr "Up" >nul
if errorlevel 1 (
    echo ❌ Algunos servicios no estan corriendo
    set /a retry+=1
    if !retry! lss %HEALTH_CHECK_RETRIES% (
        echo Reintentando... (!retry!/%HEALTH_CHECK_RETRIES%)
        goto health_retry
    )
    exit /b 1
)

REM Verificar endpoint de salud
curl -f -s http://localhost/health/ >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Endpoint de salud no responde
    set /a retry+=1
    if !retry! lss %HEALTH_CHECK_RETRIES% (
        echo Reintentando... (!retry!/%HEALTH_CHECK_RETRIES%)
        goto health_retry
    )
    exit /b 1
)

echo ✅ Todos los servicios estan saludables
exit /b 0

:check_application_integrity
echo Verificando integridad de la aplicacion...

REM Verificar configuración de Django
docker-compose -f "%COMPOSE_FILE%" exec -T web python -c "from django.conf import settings; print(settings.DEBUG)" >nul 2>&1
if errorlevel 1 (
    echo ❌ Configuracion de Django: FALLO
    exit /b 1
)
echo ✅ Configuracion de Django: OK

REM Verificar conexión a base de datos
docker-compose -f "%COMPOSE_FILE%" exec -T web python manage.py check --database default >nul 2>&1
if errorlevel 1 (
    echo ❌ Conexion a base de datos: FALLO
    exit /b 1
)
echo ✅ Conexion a base de datos: OK

REM Verificar logs de errores
docker-compose -f "%COMPOSE_FILE%" logs --tail=50 web 2>&1 | findstr /i "error exception traceback" >nul
if not errorlevel 1 (
    echo ⚠️  Se detectaron errores en los logs recientes
    exit /b 1
)
echo ✅ Logs de aplicacion: OK

exit /b 0

:perform_rollback
set reason=%~1
echo.
echo ==========================================
echo ❌ INICIANDO ROLLBACK AUTOMATICO
echo Razon: %reason%
echo ==========================================
echo [%date% %time%] ROLLBACK: %reason% >> "%LOG_FILE%"

REM Paso 1: Revertir código
echo 🔄 Revirtiendo codigo al commit anterior...
if not "%PREVIOUS_COMMIT%"=="" (
    git reset --hard %PREVIOUS_COMMIT%
    echo ✅ Codigo revertido a commit: %PREVIOUS_COMMIT%
) else (
    echo ⚠️  No se pudo identificar el commit anterior
)

REM Paso 2: Detener servicios
echo 🔄 Deteniendo servicios...
docker-compose -f "%COMPOSE_FILE%" down

REM Paso 3: Restaurar backup de base de datos
if exist "%BACKUP_FILE%" (
    echo 🔄 Restaurando backup de base de datos...
    docker-compose -f "%COMPOSE_FILE%" up -d db
    timeout /t 10 /nobreak >nul
    
    type "%BACKUP_FILE%" | docker-compose -f "%COMPOSE_FILE%" exec -T db psql -U certificados_user certificados_prod
    if errorlevel 1 (
        echo ❌ Error restaurando base de datos
        echo ⚠️  Backup disponible en: %BACKUP_FILE%
    ) else (
        echo ✅ Base de datos restaurada correctamente
    )
) else (
    echo ⚠️  No hay backup disponible para restaurar
)

REM Paso 4: Reconstruir servicios con versión anterior
echo 🔄 Reconstruyendo servicios con version anterior...
docker-compose -f "%COMPOSE_FILE%" build --no-cache
docker-compose -f "%COMPOSE_FILE%" up -d

REM Paso 5: Verificar rollback
timeout /t 15 /nobreak >nul
echo 🔄 Verificando estado despues del rollback...

call :check_health
if errorlevel 1 (
    echo ==========================================
    echo ❌ ROLLBACK FALLO
    echo Se requiere intervencion manual
    echo ==========================================
    call :send_notification "ROLLBACK_FAILED" "CRITICO: Rollback fallo. Se requiere intervencion manual inmediata."
    exit /b 1
) else (
    echo ==========================================
    echo ✅ ROLLBACK COMPLETADO EXITOSAMENTE
    echo Sistema restaurado a version anterior
    echo ==========================================
    call :send_notification "ROLLBACK_SUCCESS" "Rollback completado exitosamente. Sistema restaurado."
    exit /b 0
)

:send_notification
set status=%~1
set message=%~2
set timestamp=%date% %time%

echo [%timestamp%] NOTIFICATION: %status% - %message% >> "%APP_DIR%\logs\notifications.log"

REM Aquí se pueden agregar integraciones con Slack, email, etc.
REM Ejemplo: curl -X POST -H "Content-type: application/json" --data "{\"text\":\"%message%\"}" %SLACK_WEBHOOK_URL%

exit /b 0