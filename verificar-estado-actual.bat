@echo off
echo =========================================
echo VERIFICACION DE ESTADO ACTUAL
echo =========================================
echo.

echo Conectando al servidor...
ssh administrador@161.132.47.92 "cd dockers/sistema_certificados_drtc && echo '=== 1. Estado de contenedores ===' && docker compose -f docker-compose.prod.7070.yml ps && echo '' && echo '=== 2. Ultimos logs (sin errores) ===' && docker compose -f docker-compose.prod.7070.yml logs --tail=30 web | grep -v 'health_views' && echo '' && echo '=== 3. Probando URLs ===' && echo 'Admin:' && curl -I http://localhost:7070/admin/ 2>&1 | grep 'HTTP\|Location' && echo '' && echo 'Consulta:' && curl -I http://localhost:7070/consulta/ 2>&1 | grep 'HTTP\|Content-Type' && echo '' && echo '=== 4. Verificando CSRF y Redis ===' && grep -E '(CSRF_TRUSTED|REDIS_URL)' .env.production"

echo.
echo =========================================
echo VERIFICACION COMPLETADA
echo =========================================
echo.
echo Ahora prueba manualmente:
echo 1. Admin: https://certificados.transportespuno.gob.pe/admin/
echo 2. Consulta: https://certificados.transportespuno.gob.pe/consulta/
echo.
pause
