@echo off
echo ========================================
echo ACTUALIZACION IMPORTACION CSV
echo ========================================
echo.

echo [1/4] Subiendo cambios a GitHub...
git add templates/admin/certificates/csv_import.html
git add templates/admin/certificates/csv_validation_result.html
git add MEJORA_IMPORTACION_CSV.md
git add actualizar-csv-produccion.bat
git commit -m "Mejora interfaz importacion CSV con validacion previa y menos texto"
git push origin main

echo.
echo [2/4] Conectando al servidor...
ssh root@161.132.47.92 "cd /root && git pull"

echo.
echo [3/4] Reconstruyendo contenedor...
ssh root@161.132.47.92 "cd /root && docker-compose -f docker-compose.prod.7070.yml up -d --build"

echo.
echo [4/4] Verificando estado...
ssh root@161.132.47.92 "docker ps | grep certificados"

echo.
echo ========================================
echo ACTUALIZACION COMPLETADA
echo ========================================
echo.
echo Accede a: http://161.132.47.92:7070/admin/
echo Prueba: Participantes ^> Importar CSV
echo.
pause
