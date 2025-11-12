@echo off
REM Script para actualizar el repositorio de GitHub
REM Con los cambios de Docker Compose v2 y correcciones

echo ==========================================
echo Actualizar Repositorio GitHub
echo ==========================================
echo.

REM Verificar que estamos en un repositorio git
git status >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No estás en un repositorio Git
    echo Inicializa el repositorio primero con: git init
    pause
    exit /b 1
)

echo [OK] Repositorio Git detectado
echo.

REM Mostrar estado actual
echo Estado actual del repositorio:
git status
echo.

pause

REM Agregar todos los cambios
echo Agregando archivos modificados...
git add .

echo.
echo Archivos agregados:
git status --short
echo.

pause

REM Crear commit
echo.
set /p COMMIT_MSG="Mensaje del commit (Enter para usar mensaje por defecto): "

if "%COMMIT_MSG%"=="" (
    set COMMIT_MSG=Actualización: Docker Compose v2, corrección de permisos entrypoint.sh y documentación
)

echo.
echo Creando commit con mensaje:
echo "%COMMIT_MSG%"
echo.

git commit -m "%COMMIT_MSG%"

if errorlevel 1 (
    echo.
    echo [ADVERTENCIA] No hay cambios para commitear o hubo un error
    echo.
    pause
)

echo.
echo ==========================================
echo Push a GitHub
echo ==========================================
echo.

REM Verificar rama actual
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
echo Rama actual: %CURRENT_BRANCH%
echo.

REM Preguntar si hacer push
set /p DO_PUSH="¿Hacer push a GitHub? (S/N): "

if /i "%DO_PUSH%"=="S" (
    echo.
    echo Haciendo push a origin/%CURRENT_BRANCH%...
    git push origin %CURRENT_BRANCH%
    
    if errorlevel 1 (
        echo.
        echo [ERROR] Fallo al hacer push
        echo.
        echo Posibles causas:
        echo 1. No tienes permisos en el repositorio
        echo 2. No has configurado el remote origin
        echo 3. Necesitas autenticación
        echo.
        echo Comandos útiles:
        echo   - Ver remotes: git remote -v
        echo   - Agregar remote: git remote add origin URL_DEL_REPO
        echo   - Configurar credenciales: git config --global credential.helper store
        echo.
    ) else (
        echo.
        echo [OK] Push completado exitosamente
        echo.
        echo Tu repositorio en GitHub está actualizado
    )
) else (
    echo.
    echo Push cancelado
    echo.
    echo Para hacer push manualmente:
    echo   git push origin %CURRENT_BRANCH%
)

echo.
echo ==========================================
echo Resumen
echo ==========================================
echo.

echo Cambios principales en este commit:
echo   - Dockerfile actualizado con permisos correctos para entrypoint.sh
echo   - Scripts actualizados a Docker Compose v2 (sin guión)
echo   - Documentación completa de despliegue creada
echo   - Guías rápidas y scripts automatizados
echo.

echo Archivos principales actualizados:
echo   - Dockerfile
echo   - deploy-production.bat
echo   - EJECUTA_ESTOS_COMANDOS.bat
echo   - README_DESPLIEGUE.md
echo   - COMANDOS_PRODUCCION_2025.md
echo   - Y más...
echo.

pause
