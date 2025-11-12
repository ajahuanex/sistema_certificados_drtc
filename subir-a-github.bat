@echo off
REM Script para subir cambios a GitHub
REM Ejecutar desde Windows antes de actualizar en Ubuntu

echo ==========================================
echo Subir Cambios a GitHub
echo ==========================================
echo.

REM Verificar Git
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git no está instalado
    pause
    exit /b 1
)

echo [OK] Git detectado
echo.

REM Ver estado actual
echo Estado actual del repositorio:
git status
echo.

pause

REM Agregar todos los archivos
echo Agregando archivos al staging...
git add .

echo.
echo Archivos agregados:
git status --short
echo.

pause

REM Crear commit
echo.
echo Mensaje del commit:
echo "Actualización: Docker Compose v2, corrección permisos, dominio transportespuno.gob.pe"
echo.
echo Cambios principales:
echo - Dockerfile: chmod +x para entrypoint.sh
echo - Scripts: Docker Compose v2 (sin guión)
echo - Variables: Dominio certificados.transportespuno.gob.pe
echo - Documentación: Guías para Ubuntu y Windows
echo - Scripts: deploy-ubuntu.sh y deploy-production.bat
echo.

set /p CUSTOM_MSG="¿Usar mensaje personalizado? (Enter para usar el de arriba, o escribe tu mensaje): "

if "%CUSTOM_MSG%"=="" (
    git commit -m "Actualización: Docker Compose v2, corrección permisos, dominio transportespuno.gob.pe" -m "Cambios principales:" -m "- Dockerfile: chmod +x para entrypoint.sh" -m "- Scripts: Docker Compose v2 (sin guión)" -m "- Variables: Dominio certificados.transportespuno.gob.pe" -m "- Documentación: Guías para Ubuntu y Windows" -m "- Scripts: deploy-ubuntu.sh y deploy-production.bat"
) else (
    git commit -m "%CUSTOM_MSG%"
)

if errorlevel 1 (
    echo.
    echo [ADVERTENCIA] No hay cambios para commitear o hubo un error
    pause
    exit /b 1
)

echo.
echo [OK] Commit creado exitosamente
echo.

REM Ver rama actual
for /f "tokens=*" %%i in ('git branch --show-current') do set BRANCH=%%i
echo Rama actual: %BRANCH%
echo.

REM Hacer push
echo ==========================================
echo Push a GitHub
echo ==========================================
echo.

set /p DO_PUSH="¿Hacer push a GitHub? (S/N): "

if /i "%DO_PUSH%"=="S" (
    echo.
    echo Haciendo push a origin/%BRANCH%...
    git push origin %BRANCH%
    
    if errorlevel 1 (
        echo.
        echo [ERROR] Fallo al hacer push
        echo.
        echo Posibles causas:
        echo 1. No tienes permisos en el repositorio
        echo 2. Necesitas autenticación
        echo 3. El remote no está configurado
        echo.
        echo Comandos útiles:
        echo   git remote -v
        echo   git remote add origin URL_DEL_REPO
        echo.
        pause
        exit /b 1
    )
    
    echo.
    echo [OK] Push completado exitosamente
    echo.
    echo ==========================================
    echo Siguiente Paso: Actualizar en Ubuntu
    echo ==========================================
    echo.
    echo En tu servidor Ubuntu, ejecuta:
    echo.
    echo   cd /ruta/al/proyecto
    echo   git pull origin %BRANCH%
    echo   chmod +x deploy-ubuntu.sh
    echo   ./deploy-ubuntu.sh
    echo.
    echo O sigue la guía en: EJECUTA_EN_UBUNTU.md
    echo.
) else (
    echo.
    echo Push cancelado
    echo.
    echo Para hacer push manualmente:
    echo   git push origin %BRANCH%
    echo.
)

echo ==========================================
echo Resumen de Archivos Actualizados
echo ==========================================
echo.

echo Archivos principales:
echo   - Dockerfile (permisos corregidos)
echo   - .env.production (dominio actualizado)
echo   - .env.production.example (dominio actualizado)
echo   - deploy-ubuntu.sh (script para Ubuntu)
echo   - EJECUTA_EN_UBUNTU.md (guía para Ubuntu)
echo   - DESPLIEGUE_UBUNTU.md (guía completa)
echo   - COMANDOS_UBUNTU.md (referencia de comandos)
echo   - Y más documentación...
echo.

pause
