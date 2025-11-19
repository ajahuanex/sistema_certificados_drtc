@echo off
echo =========================================
echo LOGS DE PRODUCCION EN TIEMPO REAL
echo =========================================
echo.
echo Conectando al servidor...
echo Presiona Ctrl+C para salir
echo.

ssh administrador@161.132.47.92 "cd dockers/sistema_certificados_drtc && docker compose logs -f --tail=50"
