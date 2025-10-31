@echo off
echo ========================================
echo LEVANTANDO SERVIDOR DJANGO
echo ========================================
echo.

echo [1/2] Iniciando servidor Django...
start "Django Server" cmd /k "python manage.py runserver"

echo [2/2] Esperando 5 segundos para que el servidor inicie...
timeout /t 5 >nul

echo.
echo ========================================
echo SERVIDOR CORRIENDO
echo ========================================
echo.
echo URL: http://127.0.0.1:8000
echo.
echo Ahora:
echo 1. Abre el navegador en modo incognito (Ctrl + Shift + N)
echo 2. Ve a: http://127.0.0.1:8000/certificates/query/
echo 3. Busca DNI: 12345678
echo 4. Veras el nuevo diseno DataTable
echo.
echo Presiona cualquier tecla para abrir el navegador...
pause >nul

start chrome --incognito http://127.0.0.1:8000/certificates/query/

echo.
echo Navegador abierto en modo incognito
echo.
pause
