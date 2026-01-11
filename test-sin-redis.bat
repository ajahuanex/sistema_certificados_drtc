@echo off
echo ========================================
echo PRUEBA COMPLETA SIN REDIS
echo ========================================
echo.

echo 1. Verificando configuracion de cache...
python test-cache-config.py
if errorlevel 1 (
    echo ERROR: Fallo la configuracion de cache
    pause
    exit /b 1
)

echo.
echo 2. Construyendo contenedores...
docker-compose -f docker-compose.prod.yml build

echo.
echo 3. Iniciando servicios (sin Redis)...
docker-compose -f docker-compose.prod.yml up -d db nginx web

echo.
echo 4. Esperando que los servicios esten listos...
timeout /t 30

echo.
echo 5. Verificando estado de los servicios...
docker-compose -f docker-compose.prod.yml ps

echo.
echo 6. Probando migraciones...
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

echo.
echo 7. Creando superusuario si no existe...
docker-compose -f docker-compose.prod.yml exec web python manage.py create_superuser_if_not_exists

echo.
echo 8. Recolectando archivos estaticos...
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

echo.
echo 9. Verificando logs de la aplicacion...
docker-compose -f docker-compose.prod.yml logs --tail=20 web

echo.
echo ========================================
echo PRUEBA COMPLETADA
echo ========================================
echo.
echo La aplicacion deberia estar disponible en:
echo http://localhost:7070
echo.
echo Para ver logs en tiempo real:
echo docker-compose -f docker-compose.prod.yml logs -f web
echo.
pause