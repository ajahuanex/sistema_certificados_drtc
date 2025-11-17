@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║        🧪 PRUEBAS LOCALES - SISTEMA CERTIFICADOS          ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo.

REM Verificar si el servidor está corriendo
echo [PASO 1] Verificando si el servidor está corriendo...
echo.
powershell -Command "$response = try { Invoke-WebRequest -Uri 'http://localhost:7070/admin/' -Method Head -TimeoutSec 3 -UseBasicParsing; $true } catch { $false }; if ($response) { Write-Host '✅ Servidor corriendo en http://localhost:7070' -ForegroundColor Green } else { Write-Host '❌ Servidor NO está corriendo' -ForegroundColor Red; Write-Host '' ; Write-Host 'Inicia el servidor con:' -ForegroundColor Yellow; Write-Host '  python manage.py runserver 7070' -ForegroundColor Cyan; exit 1 }"

if errorlevel 1 (
    echo.
    echo ════════════════════════════════════════════════════════════
    echo.
    set /p START_SERVER="¿Quieres iniciar el servidor ahora? (S/N): "
    if /i "!START_SERVER!"=="S" (
        echo.
        echo Iniciando servidor en http://localhost:7070...
        start "Django Server - Puerto 7070" cmd /k "python manage.py runserver 7070"
        echo.
        echo Esperando 8 segundos para que el servidor inicie...
        timeout /t 8 >nul
        echo.
        echo ✅ Servidor iniciado
        echo.
    ) else (
        echo.
        echo Por favor inicia el servidor manualmente y vuelve a ejecutar este script.
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ════════════════════════════════════════════════════════════
echo.
echo [PASO 2] Selecciona el tipo de prueba:
echo.
echo   1. Pruebas Automatizadas Completas (Recomendado)
echo   2. Abrir URLs en Navegador (Pruebas Manuales)
echo   3. Ejecutar Script PowerShell Detallado
echo   4. Ver Guía de Pruebas
echo   5. Salir
echo.
set /p OPCION="Selecciona una opción (1-5): "

if "%OPCION%"=="1" goto AUTOMATICAS
if "%OPCION%"=="2" goto NAVEGADOR
if "%OPCION%"=="3" goto POWERSHELL
if "%OPCION%"=="4" goto GUIA
if "%OPCION%"=="5" goto FIN
goto OPCION_INVALIDA

:AUTOMATICAS
echo.
echo ════════════════════════════════════════════════════════════
echo Ejecutando pruebas automatizadas...
echo ════════════════════════════════════════════════════════════
echo.
call test-local-completo.bat
goto FIN

:NAVEGADOR
echo.
echo ════════════════════════════════════════════════════════════
echo Abriendo URLs en el navegador...
echo ════════════════════════════════════════════════════════════
echo.
echo ✅ Abriendo Admin...
start "" "http://localhost:7070/admin/"
timeout /t 2 >nul

echo ✅ Abriendo Dashboard...
start "" "http://localhost:7070/admin/dashboard/"
timeout /t 2 >nul

echo ✅ Abriendo Consulta Pública...
start "" "http://localhost:7070/consulta/"
timeout /t 2 >nul

echo ✅ Abriendo Verificación de Certificado...
start "" "http://localhost:7070/verificar/9f446c3e-6acc-4ba9-a49d-8a998a331f89/"
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo 📋 CREDENCIALES:
echo    Usuario: admin
echo    Contraseña: admin123
echo.
echo 📋 DNI DE PRUEBA:
echo    99238323 (Juan Morales Rodríguez)
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
goto FIN

:POWERSHELL
echo.
echo ════════════════════════════════════════════════════════════
echo Ejecutando script PowerShell detallado...
echo ════════════════════════════════════════════════════════════
echo.
powershell -ExecutionPolicy Bypass -File test-local-completo.ps1
goto FIN

:GUIA
echo.
echo ════════════════════════════════════════════════════════════
echo Abriendo guías de pruebas...
echo ════════════════════════════════════════════════════════════
echo.
if exist "GUIA_PRUEBAS_LOCALES.md" (
    start "" "GUIA_PRUEBAS_LOCALES.md"
    echo ✅ Guía completa abierta
)
if exist "PRUEBAS_LOCALES_RAPIDO.md" (
    start "" "PRUEBAS_LOCALES_RAPIDO.md"
    echo ✅ Guía rápida abierta
)
echo.
pause
goto FIN

:OPCION_INVALIDA
echo.
echo ❌ Opción inválida
echo.
pause
goto FIN

:FIN
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo Gracias por usar el sistema de pruebas! 🚀
echo.
echo Documentación disponible:
echo   - GUIA_PRUEBAS_LOCALES.md (Guía completa)
echo   - PRUEBAS_LOCALES_RAPIDO.md (Guía rápida)
echo   - CREDENCIALES_PRUEBA.md (Credenciales y DNIs)
echo.
echo ════════════════════════════════════════════════════════════
echo.
