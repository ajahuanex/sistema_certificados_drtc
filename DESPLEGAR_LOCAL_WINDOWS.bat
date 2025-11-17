@echo off
echo ============================================
echo DESPLIEGUE LOCAL EN WINDOWS CON DOCKER
echo Sistema de Certificados DRTC
echo ============================================
echo.

REM Verificar que Docker está corriendo
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no esta corriendo
    echo Por favor inicia Docker Desktop y vuelve a intentar
    pause
    exit /b 1
)

echo [OK] Docker esta corriendo
echo.

REM Detener contenedores existentes si los hay
echo Deteniendo contenedores existentes...
docker compose -f docker-compose.prod.yml --env-file .env.production down 2>nul
echo.

REM Construir imagenes
echo ============================================
echo PASO 1: Construyendo imagenes Docker...
echo ============================================
docker compose -f docker-compose.prod.yml --env-file .env.production build --no-cache web
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la construccion de la imagen
    pause
    exit /b 1
)
echo [OK] Imagen construida exitosamente
echo.

REM Levantar servicios
echo ============================================
echo PASO 2: Levantando servicios...
echo ============================================
docker compose -f docker-compose.prod.yml --env-file .env.production up -d
if %errorlevel% neq 0 (
    echo [ERROR] Fallo al levantar los servicios
    pause
    exit /b 1
)
echo [OK] Servicios levantados
echo.

REM Esperar a que inicien
echo ============================================
echo PASO 3: Esperando a que los servicios inicien...
echo ============================================
timeout /t 30 /nobreak
echo [OK] Servicios iniciados
echo.

REM Verificar estado
echo ============================================
echo PASO 4: Verificando estado de contenedores...
echo ============================================
docker compose -f docker-compose.prod.yml --env-file .env.production ps
echo.

REM Obtener nombre del contenedor nginx
for /f "tokens=*" %%i in ('docker ps --filter "name=nginx" --format "{{.Names}}"') do set NGINX_CONTAINER=%%i

if "%NGINX_CONTAINER%"=="" (
    echo [ERROR] No se encontro contenedor nginx
    pause
    exit /b 1
)

echo Contenedor nginx: %NGINX_CONTAINER%
echo.

REM Copiar configuracion nginx
echo ============================================
echo PASO 5: Configurando nginx...
echo ============================================
docker cp nginx.prod.http-only.conf %NGINX_CONTAINER%:/etc/nginx/nginx.conf
if %errorlevel% neq 0 (
    echo [ERROR] Fallo al copiar configuracion nginx
    pause
    exit /b 1
)
echo [OK] Configuracion nginx copiada
echo.

REM Verificar configuracion nginx
docker compose -f docker-compose.prod.yml --env-file .env.production exec nginx nginx -t
if %errorlevel% neq 0 (
    echo [ERROR] Configuracion nginx invalida
    pause
    exit /b 1
)
echo [OK] Configuracion nginx valida
echo.

REM Recolectar archivos estaticos
echo ============================================
echo PASO 6: Recolectando archivos estaticos...
echo ============================================
docker compose -f docker-compose.prod.yml --env-file .env.production exec web python manage.py collectstatic --noinput --clear
if %errorlevel% neq 0 (
    echo [ERROR] Fallo al recolectar archivos estaticos
    pause
    exit /b 1
)
echo [OK] Archivos estaticos recolectados
echo.

REM Recargar nginx
echo ============================================
echo PASO 7: Recargando nginx...
echo ============================================
docker compose -f docker-compose.prod.yml --env-file .env.production exec nginx nginx -s reload
if %errorlevel% neq 0 (
    echo [ERROR] Fallo al recargar nginx
    pause
    exit /b 1
)
echo [OK] Nginx recargado
echo.

REM Verificacion final
echo ============================================
echo PASO 8: Verificacion final...
echo ============================================
echo.
echo Verificando archivos estaticos...
docker compose -f docker-compose.prod.yml --env-file .env.production exec web ls /app/staticfiles/admin/css/ 2>nul | findstr "base.css" >nul
if %errorlevel% equ 0 (
    echo [OK] Archivos estaticos verificados
) else (
    echo [WARNING] No se pudieron verificar archivos estaticos
)
echo.

REM Mostrar logs
echo Ultimos logs de web:
docker compose -f docker-compose.prod.yml --env-file .env.production logs --tail=10 web
echo.

echo Ultimos logs de nginx:
docker compose -f docker-compose.prod.yml --env-file .env.production logs --tail=10 nginx
echo.

REM Resumen final
echo ============================================
echo DESPLIEGUE LOCAL COMPLETADO EXITOSAMENTE
echo ============================================
echo.
echo Acceso a la aplicacion:
echo   URL: http://localhost:7070/admin/
echo   Usuario: admin
echo   Contraseña: admin123
echo.
echo Comandos utiles:
echo   Ver logs: docker compose -f docker-compose.prod.yml --env-file .env.production logs -f
echo   Ver estado: docker compose -f docker-compose.prod.yml --env-file .env.production ps
echo   Detener: docker compose -f docker-compose.prod.yml --env-file .env.production down
echo   Reiniciar: docker compose -f docker-compose.prod.yml --env-file .env.production restart
echo.
echo Abre tu navegador en: http://localhost:7070/admin/
echo.
pause
