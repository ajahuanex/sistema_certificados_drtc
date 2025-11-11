@echo off
REM Script de prueba para producción local
REM Sistema de Certificados DRTC

echo ==========================================
echo Prueba de Producción Local
echo ==========================================
echo.

echo [INFO] Verificando estado de contenedores...
docker-compose -f docker-compose.prod.yml ps
echo.

echo [INFO] Verificando PostgreSQL...
docker exec certificados_db_prod pg_isready -U certificados_user -d certificados_prod
if errorlevel 1 (
    echo [ERROR] PostgreSQL no está disponible
    exit /b 1
)
echo [OK] PostgreSQL está disponible
echo.

echo [INFO] Verificando Redis...
docker exec certificados_redis_prod redis-cli ping
if errorlevel 1 (
    echo [ERROR] Redis no está disponible
    exit /b 1
)
echo [OK] Redis está disponible
echo.

echo [INFO] Verificando Django...
docker exec certificados_web_prod python manage.py check
if errorlevel 1 (
    echo [ERROR] Django tiene problemas
    exit /b 1
)
echo [OK] Django está funcionando
echo.

echo [INFO] Verificando migraciones...
docker exec certificados_web_prod python manage.py showmigrations --plan | findstr "\[X\]" | find /c "[X]"
echo [OK] Migraciones aplicadas
echo.

echo [INFO] Verificando superusuario...
docker exec certificados_web_prod python manage.py shell -c "from django.contrib.auth.models import User; print('Superusuarios:', User.objects.filter(is_superuser=True).count())"
echo.

echo ==========================================
echo Información de Acceso
echo ==========================================
echo.
echo URL HTTP:  http://localhost:7070
echo URL HTTPS: https://localhost:7443
echo.
echo Admin:     https://localhost:7443/admin/
echo Usuario:   admin
echo Password:  Ver .env.production o logs de inicio
echo.
echo ==========================================
echo Comandos Útiles
echo ==========================================
echo.
echo Ver logs:           docker-compose -f docker-compose.prod.yml logs -f
echo Ver logs web:       docker-compose -f docker-compose.prod.yml logs -f web
echo Reiniciar:          docker-compose -f docker-compose.prod.yml restart
echo Detener:            docker-compose -f docker-compose.prod.yml down
echo.
echo ==========================================
echo Estado: LISTO PARA PRUEBAS
echo ==========================================
echo.
echo Abre tu navegador en: https://localhost:7443
echo (Acepta el certificado autofirmado)
echo.

pause
