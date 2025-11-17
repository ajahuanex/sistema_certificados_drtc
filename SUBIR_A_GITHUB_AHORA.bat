@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║           📤 SUBIR CAMBIOS A GITHUB                       ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Verificar si git está instalado
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git no está instalado
    echo.
    echo Descarga Git desde: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo ✅ Git instalado correctamente
echo.

REM Verificar si es un repositorio git
if not exist ".git" (
    echo ⚠️  Este directorio no es un repositorio Git
    echo.
    set /p INIT_GIT="¿Quieres inicializar un repositorio Git? (S/N): "
    if /i "!INIT_GIT!"=="S" (
        echo.
        echo Inicializando repositorio Git...
        git init
        echo ✅ Repositorio inicializado
        echo.
    ) else (
        echo.
        echo Por favor inicializa Git manualmente con: git init
        pause
        exit /b 1
    )
)

echo ════════════════════════════════════════════════════════════
echo.
echo [PASO 1] Verificando estado del repositorio...
echo.
git status
echo.

echo ════════════════════════════════════════════════════════════
echo.
echo [PASO 2] Archivos que se subirán:
echo.
echo Nuevos archivos de pruebas locales:
echo   ✅ EMPIEZA_AQUI.md
echo   ✅ PRUEBAS_LISTAS.txt
echo   ✅ RESUMEN_PRUEBAS_LOCALES.md
echo   ✅ GUIA_PRUEBAS_LOCALES.md
echo   ✅ PRUEBAS_LOCALES_RAPIDO.md
echo   ✅ EJECUTAR_AHORA_PRUEBAS.bat
echo   ✅ test-local-completo.bat
echo   ✅ test-local-completo.ps1
echo.
echo Y todos los demás archivos del proyecto...
echo.

set /p CONTINUE="¿Continuar con el commit? (S/N): "
if /i not "%CONTINUE%"=="S" (
    echo.
    echo Operación cancelada
    pause
    exit /b 0
)

echo.
echo ════════════════════════════════════════════════════════════
echo.
echo [PASO 3] Agregando archivos al staging...
echo.

REM Agregar todos los archivos
git add .

echo ✅ Archivos agregados
echo.

echo ════════════════════════════════════════════════════════════
echo.
echo [PASO 4] Creando commit...
echo.

set /p COMMIT_MSG="Ingresa el mensaje del commit (o presiona Enter para usar el predeterminado): "
if "%COMMIT_MSG%"=="" (
    set COMMIT_MSG=feat: Agregar sistema completo de pruebas locales y scripts de despliegue
)

git commit -m "%COMMIT_MSG%"

if errorlevel 1 (
    echo.
    echo ⚠️  No hay cambios para commitear o hubo un error
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Commit creado exitosamente
echo.

echo ════════════════════════════════════════════════════════════
echo.
echo [PASO 5] Configurando repositorio remoto...
echo.

REM Verificar si ya existe un remote
git remote -v | findstr origin >nul 2>&1
if errorlevel 1 (
    echo ⚠️  No hay repositorio remoto configurado
    echo.
    echo Ejemplos de URL de repositorio:
    echo   - HTTPS: https://github.com/usuario/repositorio.git
    echo   - SSH:   git@github.com:usuario/repositorio.git
    echo.
    set /p REPO_URL="Ingresa la URL de tu repositorio GitHub: "
    
    if "!REPO_URL!"=="" (
        echo.
        echo ❌ URL no proporcionada
        echo.
        echo Para agregar el remote manualmente:
        echo   git remote add origin [URL_DEL_REPO]
        echo.
        pause
        exit /b 1
    )
    
    git remote add origin !REPO_URL!
    echo.
    echo ✅ Repositorio remoto agregado
) else (
    echo ✅ Repositorio remoto ya configurado:
    git remote -v
)
echo.

echo ════════════════════════════════════════════════════════════
echo.
echo [PASO 6] Subiendo cambios a GitHub...
echo.

REM Obtener la rama actual
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i

if "%CURRENT_BRANCH%"=="" (
    set CURRENT_BRANCH=main
    echo ⚠️  No se pudo detectar la rama, usando 'main'
)

echo Subiendo a rama: %CURRENT_BRANCH%
echo.

git push -u origin %CURRENT_BRANCH%

if errorlevel 1 (
    echo.
    echo ❌ Error al subir los cambios
    echo.
    echo Posibles soluciones:
    echo   1. Verifica tu conexión a internet
    echo   2. Verifica tus credenciales de GitHub
    echo   3. Si es la primera vez, puede que necesites autenticarte
    echo   4. Si usas SSH, verifica tu clave SSH
    echo.
    echo Para autenticarte con GitHub:
    echo   - Usa GitHub CLI: gh auth login
    echo   - O configura un Personal Access Token
    echo.
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════
echo.
echo ✅ ¡CAMBIOS SUBIDOS EXITOSAMENTE A GITHUB!
echo.
echo ════════════════════════════════════════════════════════════
echo.

REM Obtener la URL del repositorio
for /f "tokens=2 delims= " %%i in ('git remote get-url origin') do set REPO_URL=%%i

echo 📋 Información del repositorio:
echo.
echo   Rama:   %CURRENT_BRANCH%
echo   Remote: %REPO_URL%
echo.

REM Convertir URL SSH a HTTPS para el navegador
set WEB_URL=%REPO_URL%
set WEB_URL=%WEB_URL:git@github.com:=https://github.com/%
set WEB_URL=%WEB_URL:.git=%

echo   Web:    %WEB_URL%
echo.

set /p OPEN_GITHUB="¿Abrir repositorio en GitHub? (S/N): "
if /i "%OPEN_GITHUB%"=="S" (
    start "" "%WEB_URL%"
    echo.
    echo ✅ Navegador abierto
)

echo.
echo ════════════════════════════════════════════════════════════
echo.
echo 🚀 SIGUIENTE PASO: DESPLIEGUE REMOTO
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo Ahora puedes desplegar en tu servidor remoto:
echo.
echo 1. Conéctate a tu servidor Ubuntu:
echo    ssh usuario@tu-servidor-ip
echo.
echo 2. Clona el repositorio:
echo    git clone %REPO_URL%
echo.
echo 3. Ejecuta el script de despliegue:
echo    cd [nombre-del-repo]
echo    chmod +x deploy-ubuntu.sh
echo    ./deploy-ubuntu.sh
echo.
echo O revisa la guía completa:
echo    GUIA_DESPLIEGUE_REMOTO.md
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
