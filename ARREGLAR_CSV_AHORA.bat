@echo off
echo ARREGLANDO CSV AHORA...
echo.

REM Subir cambios a GitHub
git add .
git commit -m "Fix CSV import"
git push

REM Actualizar servidor
ssh root@161.132.47.92 "cd /root && git pull && docker-compose -f docker-compose.prod.7070.yml down && docker-compose -f docker-compose.prod.7070.yml up -d --build"

echo.
echo LISTO. Espera 30 segundos y prueba:
echo http://161.132.47.92:7070/admin/certificates/participant/import-csv/
pause
