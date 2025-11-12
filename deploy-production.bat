@echo off
REM Script de Despliegue a Producción
REM Sistema de Certificados DRTC

echo ==========================================
echo Despliegue a Producción
echo Sistema de Certificados DRTC
echo ==========================================
echo.

REM Verificar que Docker está corriendo
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no está corriendo
    echo Por favor inicia Docker Desktop y vuelve a intentar
    pause
    exit /b 1
)
echo [OK] Docker está corriendo

REM Verificar que existe .env.production
if not exist .env.production (
    echo [ERROR] No existe el archivo .env.production
    echo Copia .env.production.example a .env.production y configúralo
    echo.
    echo Ejecuta: copy .env.production.example .env.production
    pause
    exit /b 1
)
echo [OK] Archivo .env.production encontrado

echo.
echo ==========================================
echo Paso 1: Limpiar ambiente anterior
echo ==========================================
echo.

echo Deteniendo contenedores anteriores...
docker compose -f docker-compose.prod.yml down -v

echo.
echo ==========================================
echo Paso 2: Dar permisos a entrypoint.sh
echo ==========================================
echo.

echo Configurando permisos de ejecución...
git update-index --chmod=+x entrypoint.sh
if errorlevel 1 (
    echo [ADVERTENCIA] No se pudo usar git update-index
    echo Asegúrate de que el Dockerfile tenga: RUN chmod +x /app/entrypoint.sh
)

echo.
echo ==========================================
echo Paso 3: Construir imágenes
echo ==========================================
echo.

echo Construyendo imágenes Docker...
echo Esto puede tomar varios minutos...
docker compose -f docker-compose.prod.yml build --no-cache
if errorlevel 1 (
    echo [ERROR] Fallo al construir imágenes
    pause
    exit /b 1
)
echo [OK] Imágenes construidas exitosamente

echo.
echo ==========================================
echo Paso 4: Iniciar servicios
echo ==========================================
echo.

echo Iniciando servicios en segundo plano...
docker compose -f docker-compose.prod.yml up -d
if errorlevel 1 (
    echo [ERROR] Fallo al iniciar servicios
    echo.
    echo Ver logs con:
    echo docker compose -f docker-compose.prod.yml logs
    pause
    exit /b 1
)

echo.
echo Esperando a que los servicios estén listos...
timeout /t 30 /nobreak >nul

echo.
echo ==========================================
echo Paso 5: Verificar estado
echo ==========================================
echo.

echo Estado de los contenedores:
docker compose -f docker-compose.prod.yml ps

echo.
echo ==========================================
echo Paso 6: Verificar health check
echo ==========================================
echo.

echo Verificando health check...
timeout /t 5 /nobreak >nul

curl -f http://localhost/health/ >nul 2>&1
if errorlevel 1 (
    echo [ADVERTENCIA] Health check no responde aún
    echo Los servicios pueden estar iniciándose todavía
    echo.
    echo Verifica manualmente en: http://localhost/health/
) else (
    echo [OK] Health check respondiendo correctamente
)

echo.
echo ==========================================
echo Despliegue Completado
echo ==========================================
echo.

echo [OK] Servicios desplegados exitosamente
echo.
echo Accede a la aplicación en:
echo   - Página principal: http://localhost/
echo   - Admin:            http://localhost/admin/
echo   - Health check:     http://localhost/health/
echo   - API:              http://localhost/api/
echo.
echo Comandos útiles:
echo   - Ver logs:         docker compose -f docker-compose.prod.yml logs -f
echo   - Ver estado:       docker compose -f docker-compose.prod.yml ps
echo   - Detener:          docker compose -f docker-compose.prod.yml stop
echo   - Reiniciar:        docker compose -f docker-compose.prod.yml restart
echo.

REM Preguntar si abrir el navegador
set /p OPEN_BROWSER="¿Abrir en navegador? (S/N): "
if /i "%OPEN_BROWSER%"=="S" (
    start http://localhost/
    start http://localhost/admin/
)

echo.
echo Presiona cualquier tecla para salir...
pause >nul
