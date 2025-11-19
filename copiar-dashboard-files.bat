@echo off
echo =========================================
echo COPIANDO ARCHIVOS DEL DASHBOARD
echo =========================================
echo.

echo Copiando dashboard.css...
scp static/admin/css/dashboard.css administrador@161.132.47.92:~/dockers/sistema_certificados_drtc/static/admin/css/

echo.
echo Copiando dashboard.js...
scp static/admin/js/dashboard.js administrador@161.132.47.92:~/dockers/sistema_certificados_drtc/static/admin/js/

echo.
echo Actualizando en el contenedor...
ssh administrador@161.132.47.92 "cd dockers/sistema_certificados_drtc && docker cp static/admin/css/dashboard.css certificados_web:/app/static/admin/css/ && docker cp static/admin/js/dashboard.js certificados_web:/app/static/admin/js/ && docker compose -f docker-compose.prod.7070.yml exec -T web python manage.py collectstatic --noinput && docker compose -f docker-compose.prod.7070.yml restart web"

echo.
echo =========================================
echo ARCHIVOS COPIADOS
echo =========================================
echo.
echo Recarga el dashboard con Ctrl+Shift+R
pause
