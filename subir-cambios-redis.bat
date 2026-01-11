@echo off
echo ==========================================
echo SUBIENDO CAMBIOS DE CORRECCION REDIS
echo ==========================================
echo.

echo 1. Agregando archivos al repositorio...
git add .

echo.
echo 2. Creando commit con los cambios...
git commit -m "Fix: Configuracion Redis opcional - Cache en memoria como fallback

- Modificado config/settings/production.py con logica condicional
- Agregada variable USE_REDIS=False en .env.production  
- Redis comentado en docker-compose.prod.yml
- Sistema funciona sin Redis usando cache en memoria
- Sesiones almacenadas en base de datos
- Scripts de verificacion y despliegue creados"

echo.
echo 3. Subiendo cambios a GitHub...
git push origin main

if errorlevel 1 (
    echo ERROR: No se pudieron subir los cambios
    pause
    exit /b 1
)

echo.
echo ==========================================
echo ✅ CAMBIOS SUBIDOS EXITOSAMENTE
echo ==========================================
echo.
echo Ahora puedes conectarte al servidor remoto:
echo.
echo ssh root@161.132.47.92
echo cd /root/sistema-certificados-drtc
echo git pull origin main
echo ./desplegar-remoto-sin-redis.sh
echo.
pause