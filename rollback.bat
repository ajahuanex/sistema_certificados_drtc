@echo off
REM Script de Rollback Manual para Windows - Sistema de Certificados DRTC

setlocal enabledelayedexpansion

REM Configuración
set APP_DIR=%CD%
set BACKUP_DIR=%APP_DIR%\backups
set LOG_FILE=%APP_DIR%\logs\rollback.log
set COMPOSE_FILE=docker-compose.prod.yml

REM Crear directorio de logs si no existe
if not exist "%APP_DIR%\logs" mkdir "%APP_DIR%\logs"

echo [%date% %time%] Iniciando script de rollback manual >> "%LOG_FILE%"

:menu
cls
echo ==========================================
echo 🔄 Sistema de Rollback Manual
echo    DRTC Certificados
echo ==========================================
echo.
echo 1. Ver commits recientes
echo 2. Ver backups disponibles
echo 3. Rollback a commit especifico
echo 4. Restaurar backup de base de datos
echo 5. Rollback completo (codigo + BD)
echo 6. Verificar estado del sistema
echo 7. Rollback rapido (ultimo commit + ultimo backup)
echo 0. Salir
echo.
set /p option=Seleccione una opcion: 

if "%option%"=="1" goto list_commits
if "%option%"=="2" goto list_backups
if "%option%"=="3" goto rollback_commit
if "%option%"=="4" goto restore_backup
if "%option%"=="5" goto full_rollback
if "%option%"=="6" goto check_status
if "%option%"=="7" goto quick_rollback
if "%option%"=="0" goto end

echo Opcion invalida
pause
goto menu

:list_commits
echo.
echo 🔄 Commits recientes disponibles:
echo.
git log --oneline -10
echo.
pause
goto menu

:list_backups
echo.
echo 🔄 Backups disponibles:
echo.
if exist "%BACKUP_DIR%\*.sql.gz" (
    dir /b /o-d "%BACKUP_DIR%\*.sql.gz"
) else (
    echo No hay backups disponibles
)
echo.
pause
goto menu

:rollback_commit
echo.
set /p commit_hash=Ingrese el hash del commit: 

echo.
echo 🔄 Revirtiendo a commit: %commit_hash%
echo [%date% %time%] Rollback a commit: %commit_hash% >> "%LOG_FILE%"

REM Verificar que el commit existe
git cat-file -e %commit_hash%^{commit} 2>nul
if errorlevel 1 (
    echo ❌ Commit no valido: %commit_hash%
    pause
    goto menu
)

REM Guardar commit actual
for /f %%i in ('git rev-parse HEAD') do set current_commit=%%i
echo Commit actual: %current_commit%

REM Revertir código
git reset --hard %commit_hash%
if errorlevel 1 (
    echo ❌ Error revirtiendo codigo
    pause
    goto menu
)
echo ✅ Codigo revertido a: %commit_hash%

REM Reconstruir servicios
echo.
echo 🔄 Reconstruyendo servicios...
docker-compose -f "%COMPOSE_FILE%" down
docker-compose -f "%COMPOSE_FILE%" build --no-cache
docker-compose -f "%COMPOSE_FILE%" up -d

REM Ejecutar migraciones
echo.
echo 🔄 Ejecutando migraciones...
timeout /t 10 /nobreak >nul
docker-compose -f "%COMPOSE_FILE%" exec -T web python manage.py migrate

REM Recopilar estáticos
echo.
echo 🔄 Recopilando archivos estaticos...
docker-compose -f "%COMPOSE_FILE%" exec -T web python manage.py collectstatic --noinput

echo.
echo ✅ Rollback de codigo completado
pause
goto menu

:restore_backup
echo.
set /p backup_file=Ingrese la ruta del backup (ej: backups\backup_20250109_120000.sql.gz): 

if not exist "%backup_file%" (
    echo ❌ Archivo de backup no encontrado: %backup_file%
    pause
    goto menu
)

echo.
echo 🔄 Restaurando base de datos desde: %backup_file%
echo [%date% %time%] Restaurando backup: %backup_file% >> "%LOG_FILE%"

REM Crear backup de seguridad
echo 🔄 Creando backup de seguridad...
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set mydate=%%c%%a%%b
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set mytime=%%a%%b
set safety_backup=%BACKUP_DIR%\safety_backup_%mydate%_%mytime%.sql

docker-compose -f "%COMPOSE_FILE%" exec -T db pg_dump -U certificados_user certificados_prod > "%safety_backup%"
echo ✅ Backup de seguridad creado: %safety_backup%

REM Detener aplicación web
echo 🔄 Deteniendo aplicacion web...
docker-compose -f "%COMPOSE_FILE%" stop web nginx

REM Restaurar base de datos
echo 🔄 Restaurando base de datos...
REM Descomprimir si es .gz
echo %backup_file% | findstr /i ".gz" >nul
if not errorlevel 1 (
    7z x -so "%backup_file%" | docker-compose -f "%COMPOSE_FILE%" exec -T db psql -U certificados_user certificados_prod
) else (
    type "%backup_file%" | docker-compose -f "%COMPOSE_FILE%" exec -T db psql -U certificados_user certificados_prod
)

if errorlevel 1 (
    echo ❌ Error restaurando base de datos
    echo ⚠️  Puede restaurar el backup de seguridad: %safety_backup%
    pause
    goto menu
)

echo ✅ Base de datos restaurada correctamente

REM Reiniciar servicios
echo 🔄 Reiniciando servicios...
docker-compose -f "%COMPOSE_FILE%" start web nginx

echo.
echo ✅ Restauracion de base de datos completada
pause
goto menu

:full_rollback
echo.
echo ==========================================
echo 🔄 ROLLBACK COMPLETO
echo ==========================================
echo.

set /p commit_hash=Ingrese el hash del commit: 
set /p backup_file=Ingrese la ruta del backup: 

echo.
echo Commit: %commit_hash%
echo Backup: %backup_file%
echo.
set /p confirm=¿Esta seguro que desea continuar? (S/N): 

if /i not "%confirm%"=="S" (
    echo Rollback cancelado
    pause
    goto menu
)

REM Rollback de código
call :do_rollback_commit %commit_hash%

REM Rollback de base de datos
call :do_restore_backup "%backup_file%"

REM Verificar estado
call :do_check_status

echo.
echo ==========================================
echo ✅ ROLLBACK COMPLETO FINALIZADO
echo ==========================================
pause
goto menu

:quick_rollback
echo.
echo ==========================================
echo 🔄 ROLLBACK RAPIDO
echo ==========================================
echo.

REM Obtener último commit
for /f %%i in ('git rev-parse HEAD~1') do set previous_commit=%%i
echo Revirtiendo a commit anterior: %previous_commit%

REM Obtener último backup
for /f "delims=" %%i in ('dir /b /o-d "%BACKUP_DIR%\*.sql.gz" 2^>nul') do (
    set latest_backup=%BACKUP_DIR%\%%i
    goto found_backup
)

:found_backup
if "%latest_backup%"=="" (
    echo ⚠️  No se encontro backup reciente
    set /p continue_code=¿Continuar solo con rollback de codigo? (S/N): 
    if /i not "!continue_code!"=="S" (
        echo Rollback cancelado
        pause
        goto menu
    )
) else (
    echo Usando backup: %latest_backup%
)

echo.
set /p confirm=¿Esta seguro que desea continuar? (S/N): 

if /i not "%confirm%"=="S" (
    echo Rollback cancelado
    pause
    goto menu
)

REM Ejecutar rollback
call :do_rollback_commit %previous_commit%

if not "%latest_backup%"=="" (
    call :do_restore_backup "%latest_backup%"
)

call :do_check_status

echo.
echo ==========================================
echo ✅ ROLLBACK RAPIDO COMPLETADO
echo ==========================================
pause
goto menu

:check_status
echo.
echo 🔄 Verificando estado del sistema...
echo.

docker-compose -f "%COMPOSE_FILE%" ps

echo.
timeout /t 5 /nobreak >nul

curl -f -s http://localhost/health/ >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Endpoint de salud no responde
) else (
    echo ✅ Sistema funcionando correctamente
)

echo.
pause
goto menu

:end
echo.
echo ✅ Saliendo...
echo [%date% %time%] Script de rollback finalizado >> "%LOG_FILE%"
exit /b 0

REM ==========================================
REM FUNCIONES AUXILIARES
REM ==========================================

:do_rollback_commit
set commit=%~1
echo 🔄 Revirtiendo codigo a: %commit%
git reset --hard %commit%
docker-compose -f "%COMPOSE_FILE%" down
docker-compose -f "%COMPOSE_FILE%" build --no-cache
docker-compose -f "%COMPOSE_FILE%" up -d
timeout /t 10 /nobreak >nul
docker-compose -f "%COMPOSE_FILE%" exec -T web python manage.py migrate
docker-compose -f "%COMPOSE_FILE%" exec -T web python manage.py collectstatic --noinput
echo ✅ Rollback de codigo completado
exit /b 0

:do_restore_backup
set backup=%~1
echo 🔄 Restaurando backup: %backup%
docker-compose -f "%COMPOSE_FILE%" stop web nginx
type "%backup%" | docker-compose -f "%COMPOSE_FILE%" exec -T db psql -U certificados_user certificados_prod
docker-compose -f "%COMPOSE_FILE%" start web nginx
echo ✅ Restauracion completada
exit /b 0

:do_check_status
echo 🔄 Verificando estado...
timeout /t 5 /nobreak >nul
docker-compose -f "%COMPOSE_FILE%" ps
curl -f -s http://localhost/health/ >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Sistema con problemas
) else (
    echo ✅ Sistema OK
)
exit /b 0
