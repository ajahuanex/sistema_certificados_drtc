@echo off
echo ========================================
echo CORRIGIENDO REDIS_URL EN SERVIDOR REMOTO
echo ========================================
echo.

echo Conectando a 161.132.47.92...
echo.

ssh -p 22 administrador@161.132.47.92 "cd certificados-drtc && sed -i 's|REDIS_URL=redis://redis:6379/0|REDIS_URL=redis://:redis_password@redis:6379/0|g' .env.production && echo '=== REDIS_URL actualizado ===' && cat .env.production | grep REDIS && echo '' && echo '=== Reiniciando contenedor web ===' && docker compose restart web && echo '' && echo '=== Esperando 30 segundos ===' && sleep 30 && echo '' && echo '=== Logs del contenedor web ===' && docker compose logs --tail=20 web"

echo.
echo ========================================
echo PROCESO COMPLETADO
echo ========================================
pause
