@echo off
REM Script para subir cambios de configuración de IP a GitHub
REM Sistema de Certificados DRTC

echo ==========================================
echo Subiendo cambios de IP a GitHub
echo ==========================================
echo.

echo Agregando archivos modificados...
git add .env.production
git add SOLUCION_PASSWORD_POSTGRES.md
git add fix-postgres-password.sh

echo.
echo Creando commit...
git commit -m "fix: Actualizar ALLOWED_HOSTS con IP del servidor (161.132.47.92)"

echo.
echo Subiendo a GitHub...
git push origin main

echo.
echo ==========================================
echo Cambios subidos exitosamente
echo ==========================================
echo.
echo Ahora ejecuta en Ubuntu:
echo   cd ~/dockers/sistema_certificados_drtc
echo   git pull origin main
echo   nano .env.production  # Verifica que tenga la IP correcta
echo   docker compose -f docker-compose.prod.yml --env-file .env.production restart web
echo.
pause
