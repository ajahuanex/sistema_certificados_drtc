@echo off
chcp 65001 >nul
echo ========================================
echo 🧪 PRUEBAS LOCALES AUTOMATIZADAS
echo ========================================
echo.

set SERVER_URL=http://localhost:7070
set ADMIN_URL=%SERVER_URL%/admin/
set DASHBOARD_URL=%SERVER_URL%/admin/dashboard/
set CONSULTA_URL=%SERVER_URL%/consulta/

echo [INFO] Servidor configurado en: %SERVER_URL%
echo.

REM ============================================
REM 1. Verificar que el servidor está corriendo
REM ============================================
echo [1/10] Verificando servidor...
powershell -Command "try { $response = Invoke-WebRequest -Uri '%ADMIN_URL%' -Method Head -TimeoutSec 5; Write-Host '[OK] Servidor respondiendo' -ForegroundColor Green } catch { Write-Host '[ERROR] Servidor no responde' -ForegroundColor Red; exit 1 }"
if errorlevel 1 (
    echo.
    echo [ERROR] El servidor no está corriendo en %SERVER_URL%
    echo.
    echo Inicia el servidor con:
    echo   python manage.py runserver 7070
    echo.
    pause
    exit /b 1
)
echo.

REM ============================================
REM 2. Verificar archivos estáticos
REM ============================================
echo [2/10] Verificando archivos estáticos...
powershell -Command "try { $response = Invoke-WebRequest -Uri '%SERVER_URL%/static/admin/css/base.css' -Method Head -TimeoutSec 5; Write-Host '[OK] Archivos estáticos accesibles' -ForegroundColor Green } catch { Write-Host '[WARN] Archivos estáticos no accesibles' -ForegroundColor Yellow }"
echo.

REM ============================================
REM 3. Verificar base de datos
REM ============================================
echo [3/10] Verificando base de datos...
python manage.py check --database default >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Problemas con la base de datos
    echo.
    pause
    exit /b 1
) else (
    echo [OK] Base de datos OK
)
echo.

REM ============================================
REM 4. Verificar migraciones
REM ============================================
echo [4/10] Verificando migraciones...
python manage.py showmigrations --plan | findstr "\[ \]" >nul
if errorlevel 1 (
    echo [OK] Todas las migraciones aplicadas
) else (
    echo [WARN] Hay migraciones pendientes
    echo Ejecuta: python manage.py migrate
)
echo.

REM ============================================
REM 5. Verificar superusuario
REM ============================================
echo [5/10] Verificando superusuario...
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('[OK] Superusuario existe' if User.objects.filter(is_superuser=True).exists() else '[WARN] No hay superusuario')"
echo.

REM ============================================
REM 6. Contar registros
REM ============================================
echo [6/10] Contando registros en la base de datos...
python manage.py shell -c "from certificates.models import Event, Participant, Certificate; print(f'  - Eventos: {Event.objects.count()}'); print(f'  - Participantes: {Participant.objects.count()}'); print(f'  - Certificados: {Certificate.objects.count()}')"
echo.

REM ============================================
REM 7. Verificar configuración
REM ============================================
echo [7/10] Verificando configuración...
python manage.py check >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Problemas de configuración
    python manage.py check
    pause
    exit /b 1
) else (
    echo [OK] Configuración correcta
)
echo.

REM ============================================
REM 8. Verificar templates
REM ============================================
echo [8/10] Verificando templates...
if exist "templates\admin\dashboard.html" (
    echo [OK] Template dashboard existe
) else (
    echo [WARN] Template dashboard no encontrado
)
if exist "templates\certificates\query.html" (
    echo [OK] Template query existe
) else (
    echo [WARN] Template query no encontrado
)
echo.

REM ============================================
REM 9. Verificar archivos media
REM ============================================
echo [9/10] Verificando directorio media...
if exist "media" (
    echo [OK] Directorio media existe
    dir /b media\certificates 2>nul | find /c /v "" >nul
    if errorlevel 1 (
        echo [INFO] No hay certificados generados aún
    ) else (
        echo [OK] Hay certificados generados
    )
) else (
    echo [WARN] Directorio media no existe
    mkdir media
    mkdir media\certificates
    echo [OK] Directorios creados
)
echo.

REM ============================================
REM 10. Ejecutar tests básicos
REM ============================================
echo [10/10] Ejecutando tests básicos...
echo [INFO] Esto puede tomar unos segundos...
python manage.py test certificates.tests.test_models --verbosity=0 >nul 2>&1
if errorlevel 1 (
    echo [WARN] Algunos tests fallaron
) else (
    echo [OK] Tests básicos pasaron
)
echo.

REM ============================================
REM RESUMEN
REM ============================================
echo ========================================
echo ✅ PRUEBAS COMPLETADAS
echo ========================================
echo.
echo URLs para probar manualmente:
echo.
echo 1. Admin:      %ADMIN_URL%
echo    Usuario:    admin
echo    Contraseña: admin123
echo.
echo 2. Dashboard:  %DASHBOARD_URL%
echo.
echo 3. Consulta:   %CONSULTA_URL%
echo    DNI prueba: 99238323
echo.
echo 4. Verificar:  %SERVER_URL%/verificar/9f446c3e-6acc-4ba9-a49d-8a998a331f89/
echo.
echo ========================================
echo.

REM ============================================
REM Preguntar si abrir navegador
REM ============================================
set /p OPEN_BROWSER="¿Abrir navegador para pruebas manuales? (S/N): "
if /i "%OPEN_BROWSER%"=="S" (
    echo.
    echo Abriendo navegador...
    start "" "%ADMIN_URL%"
    timeout /t 2 >nul
    start "" "%DASHBOARD_URL%"
    timeout /t 2 >nul
    start "" "%CONSULTA_URL%"
    echo.
    echo [OK] Navegador abierto con las URLs principales
)

echo.
echo ========================================
echo 📋 SIGUIENTE PASO
echo ========================================
echo.
echo Revisa la guía completa en: GUIA_PRUEBAS_LOCALES.md
echo.
echo Para pruebas de producción local con Docker:
echo   test-produccion-local.bat
echo.
pause
