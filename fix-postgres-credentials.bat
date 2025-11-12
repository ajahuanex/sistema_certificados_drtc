@echo off
REM Script para corregir credenciales de PostgreSQL
echo ========================================
echo Corrigiendo credenciales de PostgreSQL
echo ========================================
echo.

echo [1/5] Deteniendo contenedores...
docker compose -f docker-compose.prod.yml --env-file .env.production down

echo.
echo [2/5] Eliminando volumen de PostgreSQL...
docker volume rm kiro4_postgres_data_prod 2>nul
if errorlevel 1 (
    echo Volumen no existe o ya fue eliminado
) else (
    echo Volumen eliminado exitosamente
)

echo.
echo [3/5] Recreando contenedores...
docker compose -f docker-compose.prod.yml --env-file .env.production up -d

echo.
echo [4/5] Esperando a que los servicios inicien (30 segundos)...
timeout /t 30 /nobreak

echo.
echo [5/5] Verificando estado de los servicios...
docker compose -f docker-compose.prod.yml --env-file .env.production ps

echo.
echo ========================================
echo Proceso completado
echo ========================================
echo.
echo Verifica los logs con:
echo docker compose -f docker-compose.prod.yml --env-file .env.production logs web
echo.
pause
