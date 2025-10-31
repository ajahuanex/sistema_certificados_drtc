@echo off
echo ========================================
echo REINICIANDO SERVIDOR DJANGO
echo ========================================
echo.

echo [1/4] Deteniendo procesos Python...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

echo [2/4] Limpiando cache de Django...
if exist __pycache__ rmdir /s /q __pycache__ >nul 2>&1
if exist certificates\__pycache__ rmdir /s /q certificates\__pycache__ >nul 2>&1

echo [3/4] Iniciando servidor...
start "Django Server" cmd /k "python manage.py runserver"
timeout /t 3 >nul

echo [4/4] Abriendo navegador en modo incognito...
start chrome --incognito http://127.0.0.1:8000/certificates/query/

echo.
echo ========================================
echo LISTO! El servidor esta corriendo
echo ========================================
echo.
echo Ahora:
echo 1. Busca un DNI: 12345678
echo 2. Deberas ver el nuevo diseno DataTable
echo.
pause
