@echo off
echo =========================================
echo ACTUALIZANDO CSRF EN PRODUCCION
echo =========================================
echo.

echo Conectando al servidor...
ssh administrador@161.132.47.92 "cd dockers/sistema_certificados_drtc && echo 'Deteniendo contenedores...' && docker compose down && echo '' && echo 'Actualizando archivo .env.production...' && sed -i 's|CSRF_TRUSTED_ORIGINS=.*|CSRF_TRUSTED_ORIGINS=http://localhost:7070,http://127.0.0.1:7070,http://161.132.47.92:7070,http://certificados.transportespuno.gob.pe,http://www.certificados.transportespuno.gob.pe,https://certificados.transportespuno.gob.pe,https://www.certificados.transportespuno.gob.pe|g' .env.production && echo '' && echo 'Verificando cambio...' && grep CSRF_TRUSTED_ORIGINS .env.production && echo '' && echo 'Levantando contenedores...' && docker compose up -d && echo '' && echo 'Esperando 10 segundos...' && sleep 10 && echo '' && echo 'Verificando estado...' && docker compose ps && echo '' && echo 'Logs recientes...' && docker compose logs --tail=20 web"

echo.
echo =========================================
echo ACTUALIZACION COMPLETADA
echo =========================================
echo.
echo Prueba ahora en: http://certificados.transportespuno.gob.pe/consulta/
echo.
pause
