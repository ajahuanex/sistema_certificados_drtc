@echo off
echo ========================================
echo Sistema de Certificados DRTC
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
)

REM Verificar instalación de dependencias
echo Verificando dependencias...
python -c "import django" 2>nul
if errorlevel 1 (
    echo.
    echo ERROR: Django no está instalado.
    echo Por favor ejecuta: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Ejecutar migraciones pendientes
echo.
echo Aplicando migraciones...
python manage.py migrate --noinput

REM Iniciar servidor de desarrollo
echo.
echo ========================================
echo Iniciando servidor de desarrollo...
echo Accede a: http://127.0.0.1:8000
echo Presiona Ctrl+C para detener el servidor
echo ========================================
echo.
python manage.py runserver
